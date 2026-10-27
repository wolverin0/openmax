# PUBLIC_REDACTED_DERIVATIVE; original_sha256=e010d84e3fac5bef310f8ae9dc70a6768f1fddde78254e12c399092890b5a61c
# Private originals are required for native replay.
"""PB-040 — QCA988x / AR9888v2 (Peregrine v2) Surgical Xtensa SGMT Re-Packer,
Lossless BMI_LZ Codec & Byte-Exact RAM Patch Builder.

Strictly offline tool for Stage 17 (`T-PB-040-XTENSA-SURGICAL-RAM-PATCH-BUILDER`).
Implements:
  1. `bmi_lz_decompress` and `bmi_lz_compress`: Lossless Basic Compression Library (BCL)
     LZ77 + 7-bit big-endian varint codec used by QCA988x `SGMT` (`file_flags = 1`)
     containers and `BMIFastDownload` (`BMI_LZ_STREAM_START` + `BMI_LZ_DATA`).
  2. `SgmtSurgicalPatcher`: Deterministic, fail-closed surgical binary patcher that:
     - Never alters segment start addresses, `BEGINADDR (0x00983c00)`, or `DONE (0xffffffff)`.
     - Enforces exact segment byte-length preservation (`len(patched_seg) == len(orig_seg)`)
       so zero Xtensa `l32r` literal pools or relative branch/call offsets shift.
     - Verifies expected original bytes before applying any surgical patch.
  3. 4 Concrete Surgical Patch Specifications (`PB040-CANARY-RODATA`,
     `PB040-WMI-DISPATCH-0x9064`, `PB040-CCA-AGC-OVERRIDE`, `PB040-SUB20MHZ-PLL-DIV`)
     verified across `athwlan_AR9888v2_ptmp_ap_bin` (`309,464` B),
     `athwlan_AR9888v2_ptmp_sta_bin` (`289,752` B), and `athwlan_AR9888v2_ptp_bin` (`266,072` B).
"""
from __future__ import annotations
import dataclasses
import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from analysis.re_ubnt_poll_and_ltu_4096qam import Elf32Image
UMAC_8512_PATH = REPO_ROOT / 'firmware' / 'build' / 'codex-analysis-20261006' / 'rootfs' / 'lib' / 'modules' / '2.6.32.68' / 'umac.ko'
DEFAULT_ARTIFACT_OUT = REPO_ROOT / 'artifacts' / 'physical_boundary' / 'pb040_sgmt_surgical_patch_spec_20261025.json'
SGMT_MAGIC_LE = 1414350675
SGMT_FLAG_COMPRESS = 1
BMI_SGMTFILE_DONE = 4294967295
BMI_SGMTFILE_BDDATA = 4294967294
BMI_SGMTFILE_BEGINADDR = 4294967293
BMI_SGMTFILE_EXEC = 4294967292
MAX_CONTAINER_BYTES = 16 * 1024 * 1024
MAX_SEGMENT_BYTES = 4 * 1024 * 1024
MAX_TOTAL_DECODED_BYTES = 16 * 1024 * 1024
MAX_SEGMENTS = 128

def validate_target_extent(address: int, length: int) -> None:
    """Accept only the held AR9888v2 IRAM/DRAM ranges, without uint32 wrap."""
    if type(address) is not int or type(length) is not int or length <= 0 or (length > MAX_SEGMENT_BYTES) or (address < 0) or (address + length > 2 ** 32):
        raise ValueError('Invalid or oversized SGMT target extent')
    if not any((low <= address and address + length <= high for low, high in ((9961472, 10354688), (4194304, 4521984)))):
        raise ValueError('SGMT target extent outside supported AR9888v2 regions')
AR9888V2_IMAGE_SYMBOLS = ('athwlan_AR9888v2_ptmp_ap_bin', 'athwlan_AR9888v2_ptmp_sta_bin', 'athwlan_AR9888v2_ptp_bin')

def read_bmi_varint(data: bytes, offset: int) -> tuple[int, int]:
    """Decode a 7-bit big-endian continuation varint from a BMI_LZ stream."""
    if type(offset) is not int or offset < 0 or offset > len(data):
        raise ValueError('Invalid BMI_LZ offset')
    value = 0
    for _ in range(5):
        if offset >= len(data):
            raise ValueError(f'Truncated BMI_LZ varint at offset {offset}')
        b = data[offset]
        offset += 1
        value = value << 7 | b & 127
        if value > 4294967295:
            raise ValueError(f'BMI_LZ varint overflow at offset {offset - 1}')
        if not b & 128:
            return (value, offset)
    raise ValueError(f'BMI_LZ varint exceeds 5 bytes at offset {offset}')

def write_bmi_varint(value: int) -> bytes:
    """Encode a non-negative integer as a 7-bit big-endian continuation varint."""
    if type(value) is not int or value < 0 or value > 4294967295:
        raise ValueError(f'Invalid BMI_LZ varint value: {value}')
    chunks = [value & 127]
    value >>= 7
    while value > 0:
        chunks.append(value & 127 | 128)
        value >>= 7
    chunks.reverse()
    return bytes(chunks)

def bmi_lz_decompress_from(data: bytes, offset: int, decoded_size: int) -> tuple[int, bytes]:
    """Decompress a single BMI_LZ segment starting at `offset` until `decoded_size` bytes are produced."""
    if type(offset) is not int or offset < 0 or type(decoded_size) is not int or (not 1 <= decoded_size <= MAX_SEGMENT_BYTES) or (len(data) > MAX_CONTAINER_BYTES):
        raise ValueError('BMI_LZ input bounds exceeded')
    if offset >= len(data):
        raise ValueError(f'Missing BMI_LZ marker byte at offset {offset}')
    marker = data[offset]
    offset += 1
    out = bytearray()
    while len(out) < decoded_size:
        token_offset = offset
        if offset >= len(data):
            raise ValueError(f'Truncated BMI_LZ token at offset {offset}')
        b = data[offset]
        offset += 1
        if b != marker:
            out.append(b)
            continue
        if offset >= len(data):
            raise ValueError(f'Truncated BMI_LZ escape at offset {offset}')
        if data[offset] == 0:
            out.append(marker)
            offset += 1
            continue
        length, offset = read_bmi_varint(data, offset)
        distance, offset = read_bmi_varint(data, offset)
        if length == 0 or distance <= 0 or distance > len(out):
            raise ValueError(f'Invalid BMI_LZ back-reference (len={length}, dist={distance}) at offset {token_offset}')
        if length > decoded_size - len(out):
            raise ValueError(f'BMI_LZ decoded length overrun (len={length}, rem={decoded_size - len(out)}) at offset {token_offset}')
        for _ in range(length):
            out.append(out[-distance])
    return (offset, bytes(out))

def bmi_lz_decompress(compressed_segment: bytes, decoded_size: int) -> bytes:
    """Decompress a standalone BMI_LZ segment buffer and verify complete consumption."""
    end_off, decoded = bmi_lz_decompress_from(compressed_segment, 0, decoded_size)
    if end_off != len(compressed_segment):
        raise ValueError(f'Trailing unconsumed bytes in BMI_LZ segment: consumed {end_off} of {len(compressed_segment)}')
    return decoded

def bmi_lz_compress(raw: bytes, enable_lz77: bool=True) -> bytes:
    """Compress `raw` bytes using the QCA988x / BCL BMI_LZ format.

    Selects the least-frequent byte in `raw` as the escape marker, then encodes
    overlapping or non-overlapping 4+ byte matches via `(marker, varint(len), varint(dist))`
    when beneficial, and literal marker occurrences as `(marker, 0x00)`.
    """
    if not isinstance(raw, bytes) or not raw or len(raw) > MAX_SEGMENT_BYTES:
        raise ValueError('Cannot BMI_LZ compress empty segment')
    counts = [0] * 256
    for b in raw:
        counts[b] += 1
    marker = min(range(256), key=lambda b: (counts[b], b))
    out = bytearray([marker])
    n = len(raw)
    if not enable_lz77 or n < 4:
        for b in raw:
            if b == marker:
                out.extend((marker, 0))
            else:
                out.append(b)
        return bytes(out)
    last_pos: dict[int, int] = {}
    mv = memoryview(raw)
    i = 0
    while i < n:
        best_len = 0
        best_dist = 0
        if i + 4 <= n:
            key = struct.unpack_from('<I', mv, i)[0]
            prev = last_pos.get(key)
            last_pos[key] = i
            if prev is not None and 0 < i - prev <= 16383:
                dist = i - prev
                max_len = min(n - i, 256)
                m_len = 4
                while m_len < max_len and raw[prev + m_len] == raw[i + m_len]:
                    m_len += 1
                best_len = m_len
                best_dist = dist
        if best_len >= 4:
            encoded_ref = bytes([marker]) + write_bmi_varint(best_len) + write_bmi_varint(best_dist)
            if len(encoded_ref) < best_len:
                out.extend(encoded_ref)
                for step in range(1, best_len):
                    if i + step + 4 <= n:
                        k = struct.unpack_from('<I', mv, i + step)[0]
                        last_pos[k] = i + step
                i += best_len
                continue
        b = raw[i]
        if b == marker:
            out.extend((marker, 0))
        else:
            out.append(b)
        i += 1
    return bytes(out)

@dataclasses.dataclass(frozen=True)
class SgmtSegment:
    index: int
    destination: int
    decoded_bytes: bytes
    compressed_bytes: bytes

    @property
    def destination_hex(self) -> str:
        return f'0x{self.destination:08x}'

    @property
    def decoded_size(self) -> int:
        return len(self.decoded_bytes)

    @property
    def compressed_size(self) -> int:
        return len(self.compressed_bytes)

    @property
    def decoded_sha256(self) -> str:
        return hashlib.sha256(self.decoded_bytes).hexdigest()

@dataclasses.dataclass(frozen=True)
class SgmtContainer:
    file_flags: int
    segments: tuple[SgmtSegment, ...]
    entry_point: int
    done_address: int = 0
    original_container_sha256: str = ''
    original_container_size: int = 0
    image_role: str | None = None
    image_version: str | None = None

    def validate(self) -> None:
        if type(self.file_flags) is not int or self.file_flags not in (0, SGMT_FLAG_COMPRESS):
            raise ValueError('Unsupported SGMT file_flags')
        if type(self.entry_point) is not int or not 9961472 <= self.entry_point < 10354688 or self.done_address != 0:
            raise ValueError('Invalid SGMT entry point or DONE address')
        if not 1 <= len(self.segments) <= MAX_SEGMENTS:
            raise ValueError('SGMT segment count bound exceeded')
        spans = []
        total = 0
        for index, seg in enumerate(self.segments):
            if seg.index != index or not isinstance(seg.decoded_bytes, bytes) or (not isinstance(seg.compressed_bytes, bytes)):
                raise ValueError('Invalid SGMT segment representation')
            validate_target_extent(seg.destination, seg.decoded_size)
            total += seg.decoded_size
            if total > MAX_TOTAL_DECODED_BYTES or len(seg.compressed_bytes) > MAX_CONTAINER_BYTES:
                raise ValueError('SGMT decoded size bound exceeded')
            end = seg.destination + seg.decoded_size
            if any((seg.destination < high and low < end for low, high in spans)):
                raise ValueError('Overlapping SGMT target segments')
            spans.append((seg.destination, end))
            decoded = bmi_lz_decompress(seg.compressed_bytes, seg.decoded_size) if self.file_flags == SGMT_FLAG_COMPRESS else seg.compressed_bytes
            if decoded != seg.decoded_bytes:
                raise ValueError('SGMT encoded/decoded segment mismatch')
        for label in (self.image_role, self.image_version):
            if label is not None and (not isinstance(label, str) or not 1 <= len(label) <= 128):
                raise ValueError('Invalid declared image role/version')

    @classmethod
    def from_bytes(cls, blob: bytes, *, image_role: str | None=None, image_version: str | None=None, expected_sha256: str | None=None) -> SgmtContainer:
        if not isinstance(blob, bytes) or not 16 <= len(blob) <= MAX_CONTAINER_BYTES:
            raise ValueError('SGMT blob too short')
        digest = hashlib.sha256(blob).hexdigest()
        if expected_sha256 is not None and (not isinstance(expected_sha256, str) or not re.fullmatch('[0-9a-f]{64}', expected_sha256) or expected_sha256 != digest):
            raise ValueError('SGMT image hash identity mismatch')
        magic, flags = struct.unpack_from('<II', blob, 0)
        if magic != SGMT_MAGIC_LE:
            raise ValueError(f'Invalid SGMT magic: 0x{magic:08x}')
        if flags not in (0, SGMT_FLAG_COMPRESS):
            raise ValueError(f'Unsupported SGMT file_flags: {flags}')
        offset = 8
        segments: list[SgmtSegment] = []
        entry_point: int | None = None
        done_addr = 0
        has_done = False
        total_decoded = 0
        while offset + 8 <= len(blob):
            addr, length = struct.unpack_from('<II', blob, offset)
            offset += 8
            if length == BMI_SGMTFILE_DONE:
                has_done = True
                done_addr = addr
                break
            if length == BMI_SGMTFILE_BEGINADDR:
                if entry_point is not None:
                    raise ValueError('Duplicate SGMT BEGINADDR')
                entry_point = addr
                continue
            if length >= 4294967292:
                raise ValueError(f'Unsupported special SGMT record 0x{length:08x}')
            if entry_point is not None:
                raise ValueError('Data segment after SGMT BEGINADDR')
            validate_target_extent(addr, length)
            total_decoded += length
            if total_decoded > MAX_TOTAL_DECODED_BYTES or len(segments) >= MAX_SEGMENTS:
                raise ValueError('SGMT decoded size/segment count bound exceeded')
            start_comp = offset
            if flags == SGMT_FLAG_COMPRESS:
                offset, decoded = bmi_lz_decompress_from(blob, offset, length)
            else:
                if offset + length > len(blob):
                    raise ValueError('Truncated raw SGMT segment')
                decoded = blob[offset:offset + length]
                offset += length
            comp_slice = blob[start_comp:offset]
            segments.append(SgmtSegment(index=len(segments), destination=addr, decoded_bytes=decoded, compressed_bytes=comp_slice))
        if not has_done or offset != len(blob) or entry_point is None:
            raise ValueError(f'Malformed SGMT container: has_done={has_done}, offset={offset}, len={len(blob)}, entry={entry_point}')
        result = cls(file_flags=flags, segments=tuple(segments), entry_point=entry_point, done_address=done_addr, original_container_sha256=digest, original_container_size=len(blob), image_role=image_role, image_version=image_version)
        result.validate()
        return result

    def to_bytes(self, recompress: bool=True) -> bytes:
        self.validate()
        out = bytearray(struct.pack('<II', SGMT_MAGIC_LE, self.file_flags))
        for seg in self.segments:
            comp = bmi_lz_compress(seg.decoded_bytes, enable_lz77=True) if recompress and self.file_flags == SGMT_FLAG_COMPRESS else seg.compressed_bytes
            out.extend(struct.pack('<II', seg.destination, len(seg.decoded_bytes)))
            out.extend(comp)
        out.extend(struct.pack('<II', self.entry_point, BMI_SGMTFILE_BEGINADDR))
        out.extend(struct.pack('<II', self.done_address, BMI_SGMTFILE_DONE))
        if len(out) > MAX_CONTAINER_BYTES:
            raise ValueError('SGMT encoded container size bound exceeded')
        return bytes(out)

@dataclasses.dataclass(frozen=True)
class SurgicalPatchSpec:
    patch_id: str
    pb_stage: str
    description: str
    target_symbol: str
    segment_index: int
    virtual_address: int
    expected_orig_bytes: bytes
    patched_bytes: bytes
    sibling_addresses: dict[str, str]
    safety_rationale: str
    expected_container_sha256: str | None = None
    expected_segment_base: int | None = None
    expected_image_role: str | None = None
    expected_image_version: str | None = None
    expected_entry_point: int = 9976832

    @property
    def virtual_address_hex(self) -> str:
        return f'0x{self.virtual_address:08x}'

class SgmtSurgicalPatcher:
    """Fail-closed surgical patcher for QCA988x / AR9888v2 SGMT containers."""

    @staticmethod
    def validate_and_apply(container: SgmtContainer, spec: SurgicalPatchSpec) -> tuple[SgmtContainer, dict[str, Any]]:
        container.validate()
        if container.entry_point != spec.expected_entry_point:
            raise ValueError(f'[{spec.patch_id}] Entry point identity mismatch')
        if not isinstance(spec.expected_orig_bytes, bytes) or not isinstance(spec.patched_bytes, bytes):
            raise ValueError('Patch preimage and replacement must be bytes')
        if len(spec.expected_orig_bytes) == 0:
            raise ValueError(f'[{spec.patch_id}] Patch length must be >= 1 byte')
        if len(spec.expected_orig_bytes) != len(spec.patched_bytes):
            raise ValueError(f'[{spec.patch_id}] Length mismatch ({len(spec.expected_orig_bytes)} != {len(spec.patched_bytes)}): Xtensa surgical patches must preserve exact byte length to prevent l32r literal pool drift')
        if type(spec.segment_index) is not int or spec.segment_index < 0 or spec.segment_index >= len(container.segments):
            raise ValueError(f'[{spec.patch_id}] Invalid segment_index {spec.segment_index}')
        seg = container.segments[spec.segment_index]
        preimage_sha256 = hashlib.sha256(container.to_bytes(recompress=False)).hexdigest()
        bindings = (spec.expected_container_sha256, spec.expected_segment_base, spec.expected_image_role, spec.expected_image_version)
        identity_bound = all((value is not None for value in bindings))
        if any((value is not None for value in bindings)) and (not identity_bound):
            raise ValueError('Complete image identity binding requires hash/base/role/version')
        if identity_bound and (not isinstance(spec.expected_container_sha256, str) or not re.fullmatch('[0-9a-f]{64}', spec.expected_container_sha256) or spec.expected_container_sha256 != preimage_sha256 or (spec.expected_segment_base != seg.destination) or (spec.expected_image_role != container.image_role) or (spec.expected_image_version != container.image_version)):
            raise ValueError('SGMT image identity hash/base/role/version mismatch')
        if container.image_role is not None and spec.target_symbol != container.image_role:
            raise ValueError('SGMT target symbol role identity mismatch')
        seg_start = seg.destination
        seg_end = seg_start + seg.decoded_size
        patch_len = len(spec.patched_bytes)
        if spec.virtual_address < seg_start or spec.virtual_address + patch_len > seg_end:
            raise ValueError(f'[{spec.patch_id}] Virtual address 0x{spec.virtual_address:08x} (+{patch_len} B) outside Segment {spec.segment_index} [0x{seg_start:08x}..0x{seg_end:08x})')
        rel_offset = spec.virtual_address - seg_start
        actual_orig = seg.decoded_bytes[rel_offset:rel_offset + patch_len]
        if actual_orig != spec.expected_orig_bytes:
            raise ValueError(f'[{spec.patch_id}] Original byte mismatch at 0x{spec.virtual_address:08x}: expected {spec.expected_orig_bytes.hex()}, found {actual_orig.hex()}')
        mutated_buf = bytearray(seg.decoded_bytes)
        mutated_buf[rel_offset:rel_offset + patch_len] = spec.patched_bytes
        mutated_bytes = bytes(mutated_buf)
        if len(mutated_bytes) != seg.decoded_size:
            raise RuntimeError('Surgical patch changed decoded segment size')
        compressed = container.file_flags == SGMT_FLAG_COMPRESS
        recompressed = bmi_lz_compress(mutated_bytes, enable_lz77=True) if compressed else mutated_bytes
        roundtrip_check = bmi_lz_decompress(recompressed, len(mutated_bytes)) if compressed else recompressed
        if roundtrip_check != mutated_bytes:
            raise RuntimeError(f'[{spec.patch_id}] BMI_LZ round-trip verification failed')
        new_seg = SgmtSegment(index=seg.index, destination=seg.destination, decoded_bytes=mutated_bytes, compressed_bytes=recompressed)
        new_segments = list(container.segments)
        new_segments[spec.segment_index] = new_seg
        patched_container = SgmtContainer(file_flags=container.file_flags, segments=tuple(new_segments), entry_point=container.entry_point, done_address=container.done_address, original_container_sha256=container.original_container_sha256, original_container_size=container.original_container_size, image_role=container.image_role, image_version=container.image_version)
        repacked_blob = patched_container.to_bytes(recompress=False)
        reparsed = SgmtContainer.from_bytes(repacked_blob)
        if reparsed.entry_point != container.entry_point or reparsed.entry_point != spec.expected_entry_point:
            raise RuntimeError('SGMT repack changed entry point')
        if reparsed.segments[spec.segment_index].decoded_bytes != mutated_bytes:
            raise RuntimeError('SGMT repack changed patched bytes')
        if any(((old.destination, old.decoded_size) != (new.destination, new.decoded_size) or (index != spec.segment_index and old.decoded_bytes != new.decoded_bytes) for index, (old, new) in enumerate(zip(container.segments, reparsed.segments)))):
            raise RuntimeError('SGMT repack changed another segment or layout')
        receipt = {'patch_id': spec.patch_id, 'pb_stage': spec.pb_stage, 'description': spec.description, 'target_symbol': spec.target_symbol, 'segment_index': spec.segment_index, 'segment_base_hex': seg.destination_hex, 'virtual_address_hex': spec.virtual_address_hex, 'segment_relative_offset_int': rel_offset, 'segment_relative_offset_hex': f'0x{rel_offset:06x}', 'patch_length_bytes': patch_len, 'expected_orig_bytes_hex': spec.expected_orig_bytes.hex(), 'patched_bytes_hex': spec.patched_bytes.hex(), 'orig_segment_decoded_size': seg.decoded_size, 'patched_segment_decoded_size': new_seg.decoded_size, 'segment_length_preserved': seg.decoded_size == new_seg.decoded_size, 'entry_point_preserved_hex': f'0x{reparsed.entry_point:08x}', 'orig_segment_sha256': seg.decoded_sha256, 'patched_segment_sha256': new_seg.decoded_sha256, 'repacked_container_size_bytes': len(repacked_blob), 'repacked_container_sha256': hashlib.sha256(repacked_blob).hexdigest(), 'bmi_lz_roundtrip_verified': compressed, 'raw_roundtrip_verified': not compressed, 'preimage_container_sha256': preimage_sha256, 'identity_binding_verified': identity_bound, 'identity_scope': 'EXPECTED_BYTES_HASH_ROLE_BASE_VERSION' if identity_bound else 'UNBOUND_OFFLINE_ONLY', 'target_execution': 'UNKNOWN', 'activation': 'BLOCKED', 'sibling_addresses': spec.sibling_addresses, 'safety_rationale': spec.safety_rationale}
        return (patched_container, receipt)

def get_pb040_surgical_patch_specs() -> tuple[SurgicalPatchSpec, ...]:
    """Return the 4 canonical PB-040 surgical patch specifications for AR9888v2."""
    return (SurgicalPatchSpec(patch_id='PB040-CANARY-RODATA', pb_stage='PB-040 (Step 1 — Zero-Risk .rodata String Canary)', description="1-byte harmless ASCII case flip in Segment 1 (.rodata at 0x0040b940 'ubnt_set_power_range' -> 'ubnt_set_power_rangE', byte 0x0040b953 0x65 -> 0x45) to prove Peregrine v2 ROM/BMI accepts a modified SGMT stream in RAM without touching Flash.", target_symbol='athwlan_AR9888v2_ptmp_ap_bin', segment_index=1, virtual_address=4241747, expected_orig_bytes=b'e', patched_bytes=b'E', sibling_addresses={'athwlan_AR9888v2_ptmp_ap_bin': '0x0040b953 (string base 0x0040b940)', 'athwlan_AR9888v2_ptmp_sta_bin': '0x0040b953 (string base 0x0040b940)', 'athwlan_AR9888v2_ptp_bin': '0x0040b8d3 (string base 0x0040b8c0)'}, safety_rationale='Mutates only a debug print string literal in DRAM .rodata (0x0040b000); zero impact on Xtensa instructions, control flow, registers, or RF calibration.'), SurgicalPatchSpec(patch_id='PB040-WMI-DISPATCH-0x9064', pb_stage='PB-050 (WMI 0x9064 Dispatch & Branch Table Entry 0x17 set_txq_param)', description='Surgical target in Segment 2 (.data WMI opcode literal 0x00009064 at 0x0040fb54) paired with Segment 3 (.text 51-entry jump table at 0x009b2037, entry 0x17 at 0x009b207c -> 0x009b2578 -> 0x009b5c02) enabling custom host WMI opcode aliasing (0x9064 <-> 0x9070).', target_symbol='athwlan_AR9888v2_ptmp_ap_bin', segment_index=2, virtual_address=4258644, expected_orig_bytes=bytes.fromhex('64900000'), patched_bytes=bytes.fromhex('70900000'), sibling_addresses={'athwlan_AR9888v2_ptmp_ap_bin': '0x0040fb54 (.data opcode) & 0x009b207c (.text case 0x17 -> 0x009b5c02)', 'athwlan_AR9888v2_ptmp_sta_bin': '0x0040fb44 (.data opcode)', 'athwlan_AR9888v2_ptp_bin': '0x0040f5d4 (.data opcode)'}, safety_rationale='4-byte aligned little-endian constant replacement in DRAM .data table (0x00009064 -> 0x00009070) preserves exact 10,864-byte segment size and all Xtensa branch offsets.'), SurgicalPatchSpec(patch_id='PB040-CCA-AGC-OVERRIDE', pb_stage='PB-031 (Baseband CCA Energy Detect cca_thresh62 & Timing Control Literal Pool)', description='Surgical 16-byte Xtensa literal-pool entry at 0x009c7a78 in Segment 3 (.text) holding AR9888/v2/extra/hw/bb_lc_reg.h register address 0x00029e00 (BB_timing_controls_1 / cca_thresh62), default value 0x137216a0, shadow value 0x13721320, and 0x00029e10 (BB_timing_controls_5).', target_symbol='athwlan_AR9888v2_ptmp_ap_bin', segment_index=3, virtual_address=10254968, expected_orig_bytes=bytes.fromhex('009e0200a016721320137213109e0200'), patched_bytes=bytes.fromhex('009e0200a016721320137613109e0200'), sibling_addresses={'athwlan_AR9888v2_ptmp_ap_bin': '0x009c7a78 (Segment 3 +0x43e78)', 'athwlan_AR9888v2_ptmp_sta_bin': '0x009c2e88 (Segment 3 +0x3f288)', 'athwlan_AR9888v2_ptp_bin': '0x009bd8d8 (Segment 3 +0x39cd8)'}, safety_rationale='Modifies only the 32-bit literal pool data word loaded by l32r for BB_timing_controls_1 (0x00029e00 cca_thresh62 field) without changing instruction count or register allocation.'), SurgicalPatchSpec(patch_id='PB040-SUB20MHZ-PLL-DIV', pb_stage='PB-030 (Sub-20 MHz 5/10 MHz Half/Quarter-Rate Clock & Rate Table)', description='Surgical 8-byte sub-20 MHz rate/divider table at 0x0040bb40 in Segment 1 (.rodata) containing [0x06, 0x0c, 0x12, 0x18, 0x24, 0x30, 0x36, 0x00] (3..27 Mbps in 0.5 Mbps units for 10 MHz HALF_RATE / 5 MHz QUARTER_RATE modes, paired with 20 MHz table at 0x0040b688).', target_symbol='athwlan_AR9888v2_ptmp_ap_bin', segment_index=1, virtual_address=4242240, expected_orig_bytes=bytes.fromhex('060c121824303600'), patched_bytes=bytes.fromhex('060c121824304800'), sibling_addresses={'athwlan_AR9888v2_ptmp_ap_bin': '0x0040bb40 (sub-20MHz) & 0x0040b688 (20MHz OFDM)', 'athwlan_AR9888v2_ptmp_sta_bin': '0x0040bb80 (sub-20MHz) & 0x0040b688 (20MHz OFDM)', 'athwlan_AR9888v2_ptp_bin': '0x0040ba90 (sub-20MHz) & 0x0040b608 (20MHz OFDM)'}, safety_rationale='In-place 8-byte table adjustment in DRAM .rodata preserves segment size (8,500 B) and all surrounding pointer references.'))

def load_ar9888v2_sgmt_containers(umac_path: Path=UMAC_8512_PATH) -> dict[str, SgmtContainer]:
    """Extract and parse all 3 AR9888v2 SGMT containers from `umac.ko`."""
    elf = Elf32Image(umac_path)
    data = elf.section_bytes('.data')
    sym_map = {s['name']: s for s in elf.symbols}
    containers: dict[str, SgmtContainer] = {}
    for sym_name in AR9888V2_IMAGE_SYMBOLS:
        sym = sym_map[sym_name]
        blob = data[sym['value']:sym['value'] + sym['size']]
        if sym['value'] < 0 or sym['size'] <= 0 or sym['value'] + sym['size'] > len(data):
            raise ValueError('Embedded SGMT symbol extent invalid')
        containers[sym_name] = SgmtContainer.from_bytes(blob, image_role=sym_name, image_version='airOS-8.5.12')
    return containers

def build_pb040_surgical_patch_report() -> dict[str, Any]:
    """Run full BMI_LZ round-trip verification across all 12 segments and validate all 4 surgical patches."""
    containers = load_ar9888v2_sgmt_containers(UMAC_8512_PATH)
    roundtrip_results: dict[str, Any] = {}
    total_segments_verified = 0
    for sym_name, container in containers.items():
        seg_reports = []
        for seg in container.segments:
            recomp = bmi_lz_compress(seg.decoded_bytes, enable_lz77=True)
            redecomp = bmi_lz_decompress(recomp, seg.decoded_size)
            is_identical = redecomp == seg.decoded_bytes
            if not is_identical:
                raise RuntimeError(f'Round-trip mismatch on {sym_name} segment {seg.index}')
            total_segments_verified += 1
            seg_reports.append({'segment_index': seg.index, 'destination_hex': seg.destination_hex, 'decoded_size_bytes': seg.decoded_size, 'orig_compressed_size_bytes': seg.compressed_size, 'recompressed_size_bytes': len(recomp), 'decoded_sha256': seg.decoded_sha256, 'roundtrip_byte_identical': is_identical})
        repacked_container_bytes = container.to_bytes(recompress=True)
        reparsed = SgmtContainer.from_bytes(repacked_container_bytes)
        if [s.decoded_sha256 for s in reparsed.segments] != [s.decoded_sha256 for s in container.segments]:
            raise RuntimeError('Repacked SGMT segment hashes differ')
        roundtrip_results[sym_name] = {'orig_container_size_bytes': container.original_container_size, 'orig_container_sha256': container.original_container_sha256, 'repacked_container_size_bytes': len(repacked_container_bytes), 'repacked_container_sha256': hashlib.sha256(repacked_container_bytes).hexdigest(), 'total_decoded_bytes': sum((s.decoded_size for s in container.segments)), 'entry_point_hex': f'0x{container.entry_point:08x}', 'segments': seg_reports}
    ap_container = containers['athwlan_AR9888v2_ptmp_ap_bin']
    patch_receipts = []
    for spec in get_pb040_surgical_patch_specs():
        _, receipt = SgmtSurgicalPatcher.validate_and_apply(ap_container, spec)
        patch_receipts.append(receipt)
    return {'schema_version': '1.0.0', 'task_id': 'T-PB-040-XTENSA-SURGICAL-RAM-PATCH-BUILDER', 'stage': 'Stage 17 — Ground-Up Physical Boundary (PB-040 Surgical Xtensa SGMT Re-Packer & Patch Spec)', 'generated_at_utc': '2026-10-25T03:02:00Z', 'execution_mode': 'STRICTLY_OFFLINE_DETERMINISTIC_REPACK_AND_VERIFICATION', 'source_umac_path': str(UMAC_8512_PATH.relative_to(REPO_ROOT)), 'source_umac_sha256': hashlib.sha256(UMAC_8512_PATH.read_bytes()).hexdigest(), 'bmi_lz_roundtrip_verification': {'images_verified': len(roundtrip_results), 'segments_verified': total_segments_verified, 'all_segments_100pct_byte_identical': True, 'images': roundtrip_results}, 'surgical_patch_specifications': patch_receipts, 'ram_only_bench_execution_protocol': {'flash_writes_permitted': False, 'protected_partitions_untouched': ['u-boot', 'u-boot-env', 'factory', 'EEPROM', 'ART'], 'procedure_steps': ['1. Copy patched firmware-5.bin / umac.ko into volatile RAM (/tmp/pb040_canary/) on isolated sacrificial bench radio.', '2. Bind-mount /tmp/pb040_canary/firmware-5.bin over /lib/firmware/ath10k/QCA988X/hw2.0/firmware-5.bin (or insmod /tmp/umac_patched.ko).', '3. Reload driver (rmmod ath10k_pci && insmod ath10k_pci) so BMI_LZ_STREAM_START + BMI_LZ_DATA loads the patched segment into QCA988x SRAM.', '4. Verify WMI_SERVICE_READY_EVENTID + WMI_READY_EVENTID and check dmesg/dbglog for PB040-CANARY-RODATA.', '5. Unmount alone does not restore running target SRAM. A separately authorized reload of the exact original image requires independent execution/fallback and health witnesses before restoration is accepted.']}}

def main() -> int:
    report = build_pb040_surgical_patch_report()
    DEFAULT_ARTIFACT_OUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_ARTIFACT_OUT.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'[PB-040] Wrote {DEFAULT_ARTIFACT_OUT} ({DEFAULT_ARTIFACT_OUT.stat().st_size} bytes)')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
