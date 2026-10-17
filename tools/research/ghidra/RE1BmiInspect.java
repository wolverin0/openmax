// Bounded private analysis of held host download functions; never execute target code.
// @category FuturaMAX.RE1
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import com.google.gson.GsonBuilder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class RE1BmiInspect extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1 || !currentProgram.getExecutableSHA256().equals(
                "46525dc6f8b789bf820f0713841a2a9ecdcba833300ddb1ab1ef06fc4ab6a9c5"))
            throw new IllegalArgumentException("Pinned umac module and one private output required");
        Map<String,Object> out = new LinkedHashMap<>();
        out.put("program", currentProgram.getName());
        out.put("input_sha256", currentProgram.getExecutableSHA256());
        out.put("language", currentProgram.getLanguageID().toString());
        List<Object> results = new ArrayList<>();
        DecompInterface decompiler = new DecompInterface();
        try {
            if (!decompiler.openProgram(currentProgram)) throw new IllegalStateException(decompiler.getLastMessage());
            FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                Function f = functions.next();
                if (!List.of("ol_ath_configure_target", "ol_ath_download_firmware", "ol_transfer_bin_file")
                        .contains(f.getName())) continue;
                Map<String,Object> item = new LinkedHashMap<>();
                item.put("name", f.getName()); item.put("entry", f.getEntryPoint().toString());
                DecompileResults result = decompiler.decompileFunction(f, 20, monitor);
                item.put("completed", result.decompileCompleted()); item.put("error", result.getErrorMessage());
                if (result.getDecompiledFunction() != null) item.put("decompilation", result.getDecompiledFunction().getC());
                results.add(item);
            }
        } finally { decompiler.dispose(); }
        out.put("functions", results);
        out.put("limit", "Static host download dataflow only; no runtime target memory or ROM proof.");
        Path output = Path.of(args[0]);
        Files.writeString(output, new GsonBuilder().setPrettyPrinting().create().toJson(out),
                java.nio.file.StandardOpenOption.CREATE_NEW);
        println("RE1.6 held download functions inspected: " + results.size());
    }
}
