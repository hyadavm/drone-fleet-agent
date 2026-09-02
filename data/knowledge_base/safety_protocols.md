# Drone Fleet Operating & Safety Protocols

## 1. Human-in-the-Loop (HITL) Mandate
To ensure safe aerial operations and prevent unauthorized ground maintenance dispatches:
- **Mandatory Approval:** Any agent decision classified as `SCHEDULE_REPAIR` or `RE_FLY` MUST be paused by the `hitl_gate` node.
- The decision requires explicit human confirmation via the control panel before execution.
- If rejected by the human operator, the action is logged as `ACTION_REJECTED` and overridden to standard logging.

## 2. Flight Operations & Re-Fly Constraints
- **Minimum Flight Altitude:** 15 meters for normal scanning.
- **Close Inspection (Re-Fly):** 5 meters altitude allowed only upon human authorization and clear telemetry.
- **Wind Speed Threshold:** Maximum 12 m/s. If exceeded, re-fly requests must be postponed.

## 3. Maintenance Dispatch Protocol
- Maintenance teams must receive detailed GPS coordinates, panel index, VLM defect confidence (>0.75 recommended), and retrieved manual SOP excerpt.
- Emergency shutdown dispatches require double-verification with ground sensors.
