<!-- doc-head: 962A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# PB controller migration to unified physical retest runner

Controller physical retesting delegates directly to the unified Stage959A runner.
The controller experiment role is fixed inside the frozen acquisition plan.
Default inspect/plan execution acquires no window; explicit execution must supply the acquisition interface.
Raw SHA256-bound A/A, discovery and independent holdout phases are mandatory.
Empty/error outputs, copied windows and changed configuration or source contracts fail closed.
Legacy timing arrays and imported historical reports cannot promote physical evidence.
The physical runner retests QoE; SDR timing, hMAC target actuation and multi-distance acceptance remain separate.
Existing diagnostic mathematics remains available as explicitly scoped software output.
This builder pins actual source bytes but executes no test, producer, network or device command.
Physical acceptance UNKNOWN; no new measurements, firmware activation or durable-memory ingestion.
