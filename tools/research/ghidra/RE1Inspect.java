// Offline inspection only: no program mutation, target execution or network access.
// @category FuturaMAX.RE1
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.MemoryBlock;
import com.google.gson.GsonBuilder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class RE1Inspect extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) throw new IllegalArgumentException("One evidence output path required");
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("program", currentProgram.getName());
        out.put("loader", currentProgram.getExecutableFormat());
        out.put("executable_sha256", currentProgram.getExecutableSHA256());
        out.put("language", currentProgram.getLanguageID().toString());
        out.put("compiler", currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        out.put("image_base", currentProgram.getImageBase().toString());
        List<Object> blocks = new ArrayList<>();
        for (MemoryBlock b : currentProgram.getMemory().getBlocks()) {
            Map<String, Object> item = new LinkedHashMap<>();
            item.put("name", b.getName()); item.put("start", b.getStart().toString());
            item.put("length", b.getSize()); item.put("initialized", b.isInitialized());
            blocks.add(item);
        }
        out.put("blocks", blocks);
        out.put("relocations", currentProgram.getRelocationTable().getSize());
        List<Object> selected = new ArrayList<>();
        DecompInterface decompiler = new DecompInterface();
        try {
            if (!decompiler.openProgram(currentProgram)) throw new IllegalStateException(decompiler.getLastMessage());
            FunctionIterator fs = currentProgram.getFunctionManager().getFunctions(true);
            while (fs.hasNext()) {
                Function f = fs.next();
                String n = f.getName();
                if (!(n.equals("ubnt_poll_host_ht_comm_tx") || n.equals("ubnt_poll_ht_comm_setup") ||
                      n.equals("ubnt_poll_host_set_txq_param") || n.equals("ubnt_poll_host_set_rate_override") ||
                      n.equals("ubnt_poll_host_ht_comm_prepare"))) continue;
                Map<String, Object> item = new LinkedHashMap<>();
                item.put("name", n); item.put("entry", f.getEntryPoint().toString());
                DecompileResults result = decompiler.decompileFunction(f, 40, monitor);
                item.put("completed", result.decompileCompleted());
                item.put("error", result.getErrorMessage());
                if (result.getDecompiledFunction() != null) item.put("decompilation", result.getDecompiledFunction().getC());
                selected.add(item);
            }
        } finally { decompiler.dispose(); }
        out.put("functions", selected);
        List<Object> windows = new ArrayList<>();
        MemoryBlock text = currentProgram.getMemory().getBlock(".text");
        if (text != null) {
            int[][] ranges = {{0xfe4, 0x10e0}, {0xae50, 0xafc0}, {0x13950, 0x13a20}, {0x13d50, 0x13e50}};
            for (int[] range : ranges) {
                Address at = text.getStart().add(range[0]);
                Address end = text.getStart().add(range[1]);
                while (at.compareTo(end) < 0) {
                    Instruction i = currentProgram.getListing().getInstructionAt(at);
                    Map<String, Object> item = new LinkedHashMap<>();
                    item.put("section_offset", "0x" + Long.toHexString(at.subtract(text.getStart())));
                    item.put("address", at.toString());
                    byte[] bs = new byte[4]; currentProgram.getMemory().getBytes(at, bs);
                    item.put("hex", java.util.HexFormat.of().formatHex(bs));
                    item.put("instruction", i == null ? null : i.toString());
                    windows.add(item); at = at.add(4);
                }
            }
        }
        out.put("instruction_windows", windows);
        List<Object> table = new ArrayList<>();
        MemoryBlock rodata = currentProgram.getMemory().getBlock(".rodata");
        for (int offset : new int[]{0x5eac, 0x5ec8}) {
            byte[] bytes = new byte[4]; currentProgram.getMemory().getBytes(rodata.getStart().add(offset), bytes);
            table.add(Map.of("section_offset", "0x" + Integer.toHexString(offset), "hex", java.util.HexFormat.of().formatHex(bytes)));
        }
        out.put("jump_table_entries", table);
        out.put("limits", List.of("Static analysis only", "No target execution", "Decompiler output is not independent acceptance"));
        Files.writeString(Path.of(args[0]), new GsonBuilder().setPrettyPrinting().create().toJson(out));
        println("RE1 evidence written; selected functions=" + selected.size());
    }
}
