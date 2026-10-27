#!/usr/bin/env python3
"""Render the compact human context from the frozen263..266 evidence checkpoints."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DOC='docs/CONTEXTO_MAESTRO_HUMANO_REPO_REDDIT_Y_BOUNTY.md'
RECEIPT='artifacts/autoresearch/stage267a_human_context_update_receipt.json'
SOURCES={
 'docs':'artifacts/autoresearch/stage263a_docs_budget_audit_receipt.json',
 'firmware':'artifacts/autoresearch/stage264a_all_firmware_crc32_verification_receipt.json',
 'recovery':'artifacts/autoresearch/stage265a_tester_recovery_matrix_receipt.json',
 'leaderboard':'artifacts/autoresearch/stage266a_cumulative_leaderboard_receipt.json'}


def digest(data):return hashlib.sha256(data).hexdigest()


def render(records):
    docs,fw,lb=(records[key]['summary'] for key in ('docs','firmware','leaderboard'))
    states=fw['statuses']
    lines=[
      '<!-- doc-head: Human context through Stage266A with explicit saved-evidence and release limits -->',
      'Compact local verification map; no claim of current radio, remote publication or bounty status.',
      '<!-- /doc-head -->','',
      '# Mapa humano: repositorio, firmware, Reddit y bounty','',
      'Este resumen distingue archivos verificados localmente de funcionamiento fisico.',
      'Las direcciones identifican campanas guardadas, no un inventario consultado en vivo.',
      'CONFIRMED significa comprobacion local especificada; no una aceptacion RF nueva.','',
      '## Ultimos hitos verificados','',
      '| Etapa | Resultado local | Limite de la evidencia |',
      '| :--- | :--- | :--- |',
      f"| 263A | {docs['scanned']} Markdown inventariados; {len(docs['active_failures'])} routers activos incumplian el contrato en ese corte. | Audit exit1 preservado; modificaciones posteriores requieren reescaneo. |",
      f"| 264A | {fw['images']} BIN: {states.get('VERIFIED_CONTAINER',0)} contenedores, {states.get('VERIFIED_KERNEL_ONLY',0)} kernels; {states.get('FAILED_OR_UNSUPPORTED',0)} fallos o formatos no soportados. | CRC32/SHA256 no prueban firma, placa, arranque ni recuperacion. Audit exit1 preservado. |",
      '| 265A | Dos guias sincronizadas con ocho filas de diagnostico/recuperacion. | TFTP y raw separados; ninguna escritura ni recuperacion fisica ejecutada. |',
      f"| 266A | {lb['unique_comparisons']} comparaciones / {lb['windows']} ventanas; {lb['duplicate_comparisons']} coincidencias de ID/metricas deduplicadas; {lb['rejected']} candidatos rechazados. | Datos guardados, no adquisicion nueva; topologias y metricas separadas. |",'',
      'La tabla completa esta en [leaderboard](../artifacts/autoresearch/stage266a_cumulative_leaderboard.md);',
      'el JSON conserva fuentes, hashes, punteros, cobertura y rechazos.',
      'Panel1 no tiene cuatro ventanas ABAB calificables en las fuentes inspeccionadas.',
      'Porcentajes y medias de percentiles son contrastes descriptivos por ronda, no percentiles agrupados.',
      'Los esquemas/topologias no resueltos permanecen explicitamente sin resolver.','',
      '## Firmware para testers','',
      '- [Guia universal](GUIA_UNIVERSAL_POWERBEAM_LITEBEAM_OPENMAX.md) y',
      '  [respuesta para testers](REDDIT_REPLY_FIRMWARE_TESTERS_WA_FAMILY.md): fuentes operativas del paquete publico.',
      '- Las cuatro placas WA tienen candidatos propios y kernels/DTB especificos; pertenecer a WA no basta para elegir imagen.',
      '- Stage170A produjo ocho candidatos publicos v4, con Wi-Fi/DHCP deshabilitados y opciones experimentales deshabilitadas.',
      '  La validacion fue local; no demuestra arranque/recuperacion en las cuatro placas.',
      '- Stage171A produjo kits XC/XW/XM de diagnostico, sin BIN ni modulo WA trasplantado.',
      '- Los trabajos posteriores v5/preflight no se consideran aceptados aqui sin sus recibos finales y anchors.',
      '- Acceso inicial aislado: 192.168.1.20/24; evitar conflicto de IP. El kit publico no es un perfil OTA desatendido.',
      '- Stage138A es analisis estatico: si la STA remota sigue stock airOS PtP (is_ubnt_ptp=1), conservar AP airOS compatible y convertir STA primero con perfil recuperable;',
      '  alternativa ptpmode=0, APPLY, reasociar y probar datos ARP/IPv4 antes del AP.',
      '- TFTP 192.168.1.20 requiere recovery/modelo exactos. Raw stock_airos8_wa_8711_for_mtd_firmware.bin',
      '  es otra ruta: area firmware/mtd2 solo segun mapa comprobado. El nombre 8711 no confirma version; Stage157 declara v8.7.25.',
      '- Bootloader, entorno, ART/calibracion, factory y MAC siguen protegidos. Ningun flash queda autorizado por este resumen.','',
      '## Familias y puntos de medicion guardados','',
      '| Campana | Referencia historica | Interpretacion |',
      '| :--- | :--- | :--- |',
      '| WA | .20 / .250 | Rondas RF y E2E separadas; E2E999/samples1 no demuestra mejora de ruta. |',
      '| Panel1 | .84 | Telemetria operacional antes/despues; no ABAB independiente en esos recibos. |',
      '| XC / 2XC | .198 / .253 | Rondas conjuntas no son dos replicaciones. AirPrism y placa exacta importan. |',
      '| XM | .20 en otra subred/campana | Goodput de bridge no demuestra por si solo capacidad RF; no confundir con WA .20. |',
      '| LTU | .110 | Separar Linux/SoC/bridge de ath0 OTA; LTU-Lite como AP y 4096-QAM requieren evidencia especifica. |','',
      'No se infiere identidad constante de una IP reutilizada. No se consulto ningun radio ni switch.',
      'Las cifras v2/v3/v4 de diferentes campañas no se suman como una ganancia acumulativa causal.','',
      '## Tres frentes externos','',
      '| Frente | Archivo de referencia | Estado verificable aqui |',
      '| :--- | :--- | :--- |',
      '| Repositorio | [Master index](MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md) | Trabajo local; un checkout o commit no confirma contenido remoto/publicado. |',
      '| Reddit | [Markdown](REDDIT_POST.md) / [copia HTML](reddit_post_copy.html) | Resumen bilingue y tabla; Stage196 verifico visualmente ambos temas. No se envio un post aqui. |',
      '| Bounty | [Dossier](HACKERONE_UBIQUITI_SUBMISSION_DOSSIER.md) / [reporte2](HACKERONE_REPORT_LTU_AMEDEV_KERNEL_MMAP_IOCTL.md) | Estado del portal actual UNKNOWN. Reporte2 separa hallazgos estaticos v2.4.2 de permisos runtime v2.4.0; impacto explotable no demostrado por un calculo. |','',
      'No publicar firmware extraido, configuraciones, claves o datos de clientes por inferir que .gitignore los sanea.',
      'Una exclusion de Git no elimina informacion ya presente ni es una auditoria de publicacion.','',
      '## Pendientes y criterio de cierre','',
      'Stage268A debe registrar el pytest231..268 realmente disponible y el gate literal del repositorio.',
      'Suites o etapas ausentes quedan MISSING; no se cuentan como aprobadas.',
      'Los fallos historicos de docs/contenedores no se borran cuando una prueba de deteccion pasa.',
      'No hace falta accion fisica para este trabajo documental. Cualquier flash, despliegue, publicacion',
      'o nueva adquisicion requiere su plan, evidencia y autoridad especificos.','']
    return '\n'.join(lines)


def build(root=ROOT):
    root=Path(root);records={};pins=[]
    for key,rel in SOURCES.items():
        data=(root/rel).read_bytes();obj=json.loads(data)
        expected={'docs':'263A','firmware':'264A','recovery':'265A','leaderboard':'266A'}[key]
        if obj.get('stage')!=expected:raise ValueError('wrong_stage:'+rel)
        records[key]=obj;pins.append({'path':rel,'sha256':digest(data)})
    text=render(records)
    if len(text.splitlines())>=220:raise ValueError('line_budget')
    path=root/DOC
    previous=path.read_bytes() if path.exists() else b''
    prior_receipt=root/RECEIPT
    original=None
    if prior_receipt.exists():
        old=json.loads(prior_receipt.read_bytes())
        if old.get('outputs',{}).get(DOC,{}).get('sha256')==digest(previous):
            original=old.get('previous_document')
    backup=root/'artifacts/verification/stage267a'/('previous_'+digest(previous)+'.md')
    backup.parent.mkdir(parents=True,exist_ok=True)
    if not backup.exists():backup.write_bytes(previous)
    path.write_text(text,encoding='utf-8',newline='\n')
    outputs={DOC:{'sha256':digest(path.read_bytes()),'lines':len(text.splitlines())}}
    result={'stage':'267A','task_id':'T-S267A-HUMAN-CONTEXT','static_sources':pins,'outputs':outputs,
            'previous_document':original or {'path':backup.relative_to(root).as_posix(),'sha256':digest(previous)},
            'summary':{'through_stage':'266A','human_context_lines':len(text.splitlines())},
            'boundary':{'hardware_access':False,'remote_state_checked':False,'publication':False,'new_performance_claim':False}}
    (root/RECEIPT).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT)
    args=p.parse_args(argv);print(json.dumps(build(args.root)['summary']));return 0


if __name__=='__main__':raise SystemExit(main())
