# Solar Panel Maintenance & Inspection Standard Operating Procedures (SOP)

## 1. Overview
This document outlines standard maintenance procedures for aerial solar PV array inspections. Inspections classify anomalies by severity to dictate operational workflow.

---

## 2. Anomaly Classification & Action Matrix

### 2.1 Clean / Normal Condition (Severity: NONE)
- **Visual Pattern:** Uniform silicon reflectance, intact gridlines, clean glass surface.
- **Diagnosis:** Operational, optimal efficiency (>98%).
- **Standard Action:** `LOG_ONLY`
- **Procedure:** Record inspection timestamp, log GPS coordinates of panel array, update fleet status log.

### 2.2 Surface Dirt & Dust / Soiling (Severity: LOW to MEDIUM)
- **Visual Pattern:** Matte brown/gray layer obscuring antireflective coating, localized dirt streaks.
- **Diagnosis:** Soiling accumulation reducing power output by 5% - 15%.
- **Standard Action:** `SCHEDULE_REPAIR` (Human Confirmation Required)
- **Procedure:** Schedule automated robotic water cleaning or manual maintenance crew within 72 hours.

### 2.3 Micro-cracks & Physical Damage (Severity: HIGH)
- **Visual Pattern:** Fine spiderweb fractures, glass shattering, or mechanical impact marks.
- **Diagnosis:** Structural micro-crack; risks hotspot formation, moisture ingress, and bypass diode degradation.
- **Standard Action:** `SCHEDULE_REPAIR` (Human Confirmation Required)
- **Procedure:** Immediate dispatch of certified electrician team for module isolation and replacement within 24 hours.

### 2.4 Thermal Hotspots (Severity: CRITICAL)
- **Visual Pattern:** Discolored cell surface, burn marks, localized thermal overload pattern.
- **Diagnosis:** Active electrical short or failed bypass diode creating severe fire risk.
- **Standard Action:** `SCHEDULE_REPAIR` (Human Confirmation Required)
- **Procedure:** Emergency electrical disconnect signal sent to inverter, priority maintenance dispatch.

### 2.5 Bird Debris & Vegetation Obstruction (Severity: MEDIUM)
- **Visual Pattern:** Opaque white/brown spots, shadowing over multi-cell string.
- **Diagnosis:** Localized cell shadowing causing reverse-bias heating.
- **Standard Action:** `RE_FLY` or `SCHEDULE_REPAIR` (Human Confirmation Required)
- **Procedure:** Request targeted low-altitude re-fly (5m altitude) to confirm shadowing boundaries or schedule spot cleaning.
