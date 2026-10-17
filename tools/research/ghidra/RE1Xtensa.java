// Offline AP SGMT import and common-ISA inspection; private Ghidra database only.
// @category FuturaMAX.RE1
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.MemoryBlock;
import com.google.gson.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;

public class RE1Xtensa extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) throw new IllegalArgumentException("Manifest and output path required");
        Path manifest = Path.of(args[0]).toAbsolutePath().normalize();
        Path parent = manifest.getParent();
        JsonArray records = JsonParser.parseString(Files.readString(manifest)).getAsJsonArray();
        for (JsonElement element : records) {
            JsonObject r = element.getAsJsonObject();
            Path payload = parent.resolve(r.get("file").getAsString()).normalize();
            if (!payload.getParent().equals(parent)) throw new IllegalArgumentException("Payload escapes runtime");
            byte[] data = Files.readAllBytes(payload);
            String hash = HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(data));
            if (data.length != r.get("size").getAsInt() || !hash.equals(r.get("sha256").getAsString()))
                throw new IllegalArgumentException("Payload hash/length mismatch");
            Address at = toAddr(r.get("start").getAsLong());
            MemoryBlock block = currentProgram.getMemory().getBlock(at);
            if (block == null) block = currentProgram.getMemory().createInitializedBlock(
                "SGMT_" + at, at, new java.io.ByteArrayInputStream(data), data.length, monitor, false);
            else if (block.getSize() != data.length) throw new IllegalArgumentException("Unexpected existing block");
            block.setRead(true); block.setExecute(true);
            currentProgram.getMemory().setBytes(at, data);
        }
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("language", currentProgram.getLanguageID().toString());
        result.put("context", "Default common-Xtensa; LITBASE is NOT established from runtime");
        List<Object> windows = new ArrayList<>();
        for (long start : new long[]{0x983c00L, 0x9b0620L, 0x9b1604L, 0x9b1eecL,
                                    0x9b68ccL, 0x9b7264L, 0x9b77c4L}) {
            Address at = toAddr(start), end = at.add(128);
            disassemble(at);
            Map<String, Object> w = new LinkedHashMap<>(); w.put("start", "0x" + Long.toHexString(start));
            List<Object> instructions = new ArrayList<>();
            while (at.compareTo(end) < 0) {
                Instruction i = currentProgram.getListing().getInstructionAt(at);
                if (i == null) { w.put("stop_address", at.toString()); w.put("stop_reason", "No defined instruction; not necessarily decoder failure"); break; }
                Map<String, Object> row = new LinkedHashMap<>();
                row.put("address", "0x" + Long.toHexString(at.getOffset()));
                row.put("length", i.getLength()); row.put("hex", HexFormat.of().formatHex(i.getBytes()));
                row.put("instruction", i.toString()); instructions.add(row); at = at.add(i.getLength());
            }
            w.put("instructions", instructions); windows.add(w);
        }
        result.put("windows", windows);
        List<Object> slots = new ArrayList<>();
        for (long slot : new long[]{0x406414L, 0x406564L, 0x406568L})
            slots.add(Map.of("address", "0x" + Long.toHexString(slot), "mapped", currentProgram.getMemory().contains(toAddr(slot))));
        result.put("indirect_slots", slots);
        result.put("limits", List.of("Syntax comparison only, not QCA-core qualification", "No target execution", "No ROM or pointer values invented"));
        Files.writeString(Path.of(args[1]), new GsonBuilder().setPrettyPrinting().create().toJson(result));
        println("RE1 common-Xtensa inspection complete; windows=" + windows.size());
    }
}
