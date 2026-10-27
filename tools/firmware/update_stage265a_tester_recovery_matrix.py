#!/usr/bin/env python3
"""Synchronize a gated bilingual recovery matrix from held Stage138/157 evidence."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUIDES = ('docs/GUIA_UNIVERSAL_POWERBEAM_LITEBEAM_OPENMAX.md',
          'docs/REDDIT_REPLY_FIRMWARE_TESTERS_WA_FAMILY.md')
RAW = 'firmware/openwrt/pbe5ac_gen2_ptp_kit/stock_airos8_wa_8711_for_mtd_firmware.bin'
SOURCES = ('artifacts/autoresearch/stage138a_ptp_sta_data_gate_verdict.json',
           'artifacts/autoresearch/stage157a_canonical_step1_stock_mtd_builder_receipt.json')
PINS = ('94a9e4264fd7f2b3d644654b4cc4c0183b32d99454c4b7f08634a42d16ce643a',
        '1ac2a9a2875da91edb8683018b5a693b87c96b79b32afd07fee526242539b172')
RAW_PIN = '2d4838ff638d6726dbbd0587bc538856c777d592b4b7593f88a96d0300801c49'
START, END = '<!-- stage265a-recovery:start -->', '<!-- stage265a-recovery:end -->'
MATRIX = '''## Recuperación y diagnóstico / Troubleshooting and recovery

Esta matriz es un plan condicionado, no una orden de flash ni prueba de recuperación.
This is a gated plan, not an executed flash or evidence of successful recovery.

| Síntoma / Symptom | Diagnóstico sin escritura / Read-only diagnosis | Ruta y condición de parada / Route and stop condition |
| :--- | :--- | :--- |
| Sin Wi-Fi tras imagen pública / No wireless after public image | Wi-Fi y DHCP empiezan deshabilitados; Ethernet directo aislado, PC en 192.168.1.0/24 con IP distinta de .20. Verificar enlace, alimentación PoE correcta y ARP. | Administración inicial 192.168.1.20/24; evitar otro equipo con esa IP. No usar este kit para conversión remota desatendida. |
| No responde la administración / Management unreachable | Revisar subred, ARP, VLAN, cable y MAC/placa; no resetear repetidamente ni adivinar una IP de producción. | Si la unidad sigue accesible, guardar configuración y hashes. No escribir sin identificar modelo/revisión e imagen exactos. |
| Boot fallido / Failed boot | Recuperación U-Boot TFTP en red Ethernet local aislada; confirmar el modo recovery según el modelo exacto. | TFTP objetivo 192.168.1.20, PC por ejemplo 192.168.1.10/24. Solo firmware factory/vendor validado para esa placa, tamaño y hash comprobados; no sysupgrade ni imagen raw. Detener si el bootloader/modelo no están confirmados. |
| Volver de OpenWrt a airOS / Return from OpenWrt to airOS | Leer /proc/mtd y mapa exacto; verificar nombre firmware y geometría, backups y hashes de bootloader/env/cfg/ART, salud y recovery. | La imagen raw stock_airos8_wa_8711_for_mtd_firmware.bin corresponde al área firmware (mtd2 SOLO en el mapa validado). No es un archivo TFTP, factory o sysupgrade; no adivinar /dev/mtd2 por número. Escritura bloqueada hasta autorización específica y recuperación demostrada. |
| Asociación sin ARP/IPv4 / Associated but no data | Separar EAPOL/L2 de datos bidireccionales; revisar WDS 4-address, bridge y Stage138A is_ubnt_ptp=1. | Si la STA sigue stock PtP, conservar AP airOS compatible y convertir STA remota primero con perfil OTA recuperable validado; alternativa radio.1.ptpmode=0, APPLY, reasociar y verificar ARP/IPv4 ANTES del AP. Stage138A es evidencia estática, no prueba de flash OTA. |
| Datos unidireccionales / One-way forwarding | Revisar ETH_P_TEB 0x6558, módulo/ABI, AP_VLAN y admitter dinámico phy*-ap0, rutas y puentes. | No atribuirlo solo a señal RF ni forzar puertos desconocidos al bridge. Los kits públicos no aportan watchdog OTA. |
| Menor velocidad, latencia o reinicios / Slow link, tails or resets | Comparar carga/RF/canal legales, CPU/RAM, pérdidas, resets y getters; iperf3 en texto (sin -J en MIPS BE). | Champion es opt-in; apagar una bandera no restaura UCI/sysctl anteriores. Restaurar snapshot conocido con autorización, medir de nuevo y conservar la regresión. |
| Archivo o hash distinto / Wrong file or digest | Comparar SHA256SUMS, perfil exacto, longitud, CRC y origen; coincidencia de familia WA no basta. | STOP: no flashear, renombrar otra placa ni tocar bootloader/env/calibración/ART/factory/MAC. |

Raw local: 10,092,544 bytes; SHA256 `2d4838ff638d6726dbbd0587bc538856c777d592b4b7593f88a96d0300801c49`.
El nombre histórico dice 8711, pero Stage157A declara como fuente WA.v8.7.25.bin:
no inferir versión ni compatibilidad del nombre; procedencia/placa requieren validación separada.
The historical filename is not a version or compatibility guarantee.
TFTP y raw son rutas distintas; ninguna requiere tocar radios para revisar esta guía.
'''


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_section(text):
    if START in text or END in text:
        if text.count(START) != 1 or text.count(END) != 1 or text.index(END) < text.index(START):
            raise ValueError('ambiguous_recovery_markers')
        text = text[:text.index(START)] + text[text.index(END)+len(END):]
    text = text.rstrip()+'\n\n'+START+'\n'+MATRIX+END+'\n'
    lines=text.splitlines()
    if len(lines)>=220 or sum('<!-- doc-head:' in line for line in lines)!=1 or not lines[0].startswith('<!-- doc-head:'):
        raise ValueError('guide_budget_or_header')
    lines[0]=lines[0].replace(' -->','; Stage265A gated recovery matrix -->') if 'Stage265A' not in lines[0] else lines[0]
    return '\n'.join(lines)+'\n'


def build(root=ROOT):
    root=Path(root)
    source_rows=[]
    for rel,pin in zip(SOURCES,PINS):
        path=root/rel
        actual=digest(path)
        if actual!=pin:raise ValueError('source_drift:'+rel)
        source_rows.append({'path':rel,'sha256':actual})
    data=(root/RAW).read_bytes()
    if len(data)!=10092544 or hashlib.sha256(data).hexdigest()!=RAW_PIN:
        raise ValueError('raw_recovery_image_missing_or_drifted')
    source_rows.append({'path':RAW,'sha256':RAW_PIN,'bytes':len(data)})
    updates={rel:replace_section((root/rel).read_text(encoding='utf-8-sig')) for rel in GUIDES}
    outputs={}
    for rel,text in updates.items():
        (root/rel).write_text(text,encoding='utf-8',newline='\n')
        outputs[rel]={'sha256':digest(root/rel),'lines':len(text.splitlines())}
    result={'stage':'265A','task_id':'T-S265A-TESTER-RECOVERY-MATRIX','static_sources':source_rows,
            'outputs':outputs,'summary':{'matrix_rows':8,'guides':2,'raw_version_filename_mismatch_disclosed':True},
            'boundary':{'hardware_access':False,'flash_executed':False,'recovery_tested':False,
                        'board_match_required':True,'mtd_number_not_portable':True}}
    path=root/'artifacts/autoresearch/stage265a_tester_recovery_matrix_receipt.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    args=p.parse_args(argv)
    try:print(json.dumps(build(args.root)['summary']));return 0
    except (OSError,ValueError) as exc:print(str(exc));return 1


if __name__=='__main__':raise SystemExit(main())
