```text
┌──────────────────────────────────────────────────────────────┐
│   ___                  _     ___ _ _                         │
│  / __|_ __  __ _ _ _ _| |_  | __(_) |_ _ _  ___ ___ ___      │
│  \__ \ '  \/ _` | '_/ _`  _| | _|| |  _| ' \/ -_|_-<_-<      │
│  |___/_|_|_\__,_|_| \__,_|_| |_| |_|\__|_||_\___/__/__/      │
│                                                              │
│   ♥ ---/\_/\_----/\_/\/\_----/\_/\_---  [ 125 BPM | 98% HR ] │
└──────────────────────────────────────────────────────────────┘


---
```
# Smart Fitness Session Analyzer Part 2


## 1. Overview
The Smart Fitness Session Analyzer is a Python application that processes, validates, analyzes, and classyfies wearable sensor time-series data collected during exercise sessions. Wearable fitness monitors generate biometric data like
- Heart rate
- Skin response
- Body temperature
- Activity level
- Signal quality

The application ingests simulated multi-sensor observation windows, validates readings against physical and signal quality constraints, compares session metrics against individual participant reference baselines, detects recovery trends, and classifies overall session intensity.

## 2. Repository Structure
The project is divided into modular Python files.

```
smart-fitness-analyzer/
│  
├── utils.py			# Standalone helper functions for validation, math, and report formatting
├── models.py			# Domain classes (Participants, Observation, Session)
├── analyzer.py			# Analysis hierarchy (BaseAnalyzer and FitnessAnalyzer)
├── main.py				# Application running all scenarios
├── tests.py			# Unit test suite verifying logic across scenarios and edge cases
├── vvv NEW vvv
├── exceptions.py		# Defines custom exception classes for error handling
├── validators.py		# Encapsulates regular expression pattern
├── loader.py       	# Handles CSV file ingestion using Python's csv module, type conversion, participant mapping, and rejected record tracking
├── reporter.py			# Exports the final analysis results and error logs into formatted files
└── README.md			# Documentation
```
The codebase is decomposed into specialized modules to improve readability and maintainability:
* ```utils.py``` contains foundational, non-class utility functions for sensor schema validation, safe mathematical averaging, relative intensity calculations, and string report formatting.
* ```models.py``` houses core data models (Participant, Observation, Session) encapsulating participant baselines and t ime-series sensor windows.
* ```analyzer.py``` implements the analysis class hierarchy (BaseAnalyzer, FitnessAnalyzer) that processes session objects and applies classification rules.

## 3. Class Design
The application is structured around four primary classes, each adhering to the Single Responsibility Principle:</br> </br>
```Participant``` manages individual user demographic data and personal baseline reference values (```resting_hr```, ```max_hr```). It serves as the personal benchmark for computing relative exertion and intensity percentages.</br> </br>
```Observation``` encapsulates a single time-window sensor reading. It parses raw measurement dictionaries, validates sensor ranges, and exposes cleaned, ready-only biometric properties.</br> </br>
```Session``` represents a complete workout session composed of sequential ```Observation``` windows. It manages time-series collections, calculates summary statistics (min, max, avg), filters invalid observations, and evaluates tail-end recovery trends.</br> </br>
```BaseAnalyzer``` & ```FitnessAnalyzer``` evaluates session metrics and outputs structured classification dictionaries and rationales. It applies classification algorithms (resting, moderate activity, high activity, recovering, or insufficient data) and checks data completeness.
```RejectedRecord``` encapsulates metadata for CSV rows rejected during loading. Formats error entries for export into ```rejected_records.txt```.

## 4. Object-Oriented Design
**Composition**\
Demonstrated in the ```Session``` class, which contains a collection of ```Observation``` objects and refrences a ```Participant``` object. A ```Session``` owns its observations and manages their lifecycles during analysis.</br> </br>
**Encapsulation**\
Demonstrated in ```Observation``` and ```Participant``` classes through protected attributes (e.g., ```_raw_data```, ```_resting_hr```, ```_max_hr```, ```_is_valid```). Access to these attributes is controlled via read-only ```@property``` decorators, preventing unauthorized direct modification.</br> </br>
**Inheritance & Method Overriding**\
```BaseAnalyzer``` serves as an abstract base class defining the ```analyze(session)``` interface. ```FitnessAnalyzer``` inherits from ```BaseAnalyzer``` and overrides ```analyze()``` to implement fitness-specific classification logic and threshold rules.</br> </br>
**Custom Exception Hierarchy**
Extends standard library error handling by defining two explitic exception classes derived from ```ValueError```:
```
Class InvalidIdentifierError(ValueError):
	pass

class InvalidRecordError(ValueError):
	pass
```
**Class Methods & Static Methods**
* Class Method (```@classmethod```):
	* ```Participant.from_profile(profile_dict, age)``` acts as factory constructor converting raw profile dictionaries from ```data_generator.py``` into ```Participant``` instances.
	* ```FitnessAnalyzer.create_default()``` acts as an alternative constructor for instantiating the analyzer.
* Static Method (```@staticmethod)```:
	*  ```FitnessAnalyzer.is_sufficient_data(usable_count), total_count)``` provides a utility function to determine if valid readings meet the minimum 50% data threshold without accessing instance state.

## 5. Regular Expression & Validation Rules
**Regular Expression Rules**
Identifiers in CSV files must strictly match anchored patterns:
* **Participant ID**: ```^P\d{3}$``` (Matches ```P``` followed by exactly three digits, e.g., ```P001, P002```).
* **Session ID**: ```^FIT-\d{4}-\d{3}$``` (Matches ```FIT-``` followed by 4-digit year and 3-digit sequence, e.g., ```FIT-2026-001```).
**Biometric Range & Data Quality Rules**
A sensor observation row is rejected or marked invalid if:
* Any required CSV column is missing or blank.
* Biometric fields fail numeric float conversion.
* Physiological values fall outside physical bounds:
	* ```heart_rate```: 30.0 to 220.0 bpm
 	* ```activity_level```: 0.0 to 1.0
  	* ```temperature```: 20.0 to 45.0 °C
* ```signal_quality``` falls below ```0.70```.
* Participant ID does not exist in loaded participant profiles.

## 6. Assumptions & Classification Logic
**Data Validation Ruleset**\
An observation is flagged as invalid if:
* Any required key is missing from the dictionary.
* ```signal_quality``` is below 0.70.
* Biometric values fall outside physiological limits (e.g., heart rate < 30 or > 220 bpm, activity level < 0.0 or > 1.0.

**Classification Logic & Rules**
* **Insufficient Data**: Triggered if less than 50% of session observations are valid.
* **Resting**: Relative Heart Rate < 55% of max HR.
* **Moderate Activity**: 55% <= Relative Heart Rate < 75% of max HR.
* **High Activity**: Relative Heart Rate >= 75% of max HR.
* **Recovering**: Triggered when a session classified as moderate or high activity exhibits a significant drop in average heart rate (final 30% window avg HR drops below 85% of initial 70% of max HR.

## 7. Installation & Running Instructions
**Prerequisites**
* Python 3.8 or higher
* Only uses the Python standard library (no ```pandas```, ```numpy```, or any third-party packages required).
 > [!NOTE]
>On Windows systems where ```python3```is not aliased, use ```python main.py```insead.

**Instructions**
1. Clone the repository
	```
	git clone https://github.com/Funeralpyre-git/smart-fit-analyzer-part-2
	cd /smart-fit-analyzer-part-2
	```
2. Run the main application:
	```
	python3 main.py --profiles participants.csv --sessions fitness_sessions.csv fitness_sessions_invalid.csv --output output
	```
3. Run the test suite:
	```
	python3 -m unittest tests.py
	```
## 8. Example Output
**Console Completion Summary**
```
Loading profiles...
Loading sessions...
Analyzing sessions...
Generating report...

==================================================
           PROCESSING COMPLETE
==================================================
Accepted Sessions Processed: 8
Rejected Records Logged    : 14
Report Directory           : C:\Users\User\Projects\smart-fit-analyzer-part-2\output
==================================================
```
**Sample Output File 1: `output/analysis_summary.csv`**
```
FIT-2026-001,P001,6,6,resting,68.83,0.09
FIT-2026-002,P002,6,6,moderate_activity,102.0,0.5
FIT-2026-003,P003,6,6,moderate_activity,132.5,0.75
FIT-2026-004,P001,6,6,recovering,113.17,0.55
FIT-2026-005,P002,0,5,insufficient_data,N/A,N/A
FIT-2026-101,P001,2,4,resting,98.0,0.44
FIT-2026-102,P002,0,3,insufficient_data,N/A,N/A
FIT-2026-103,P003,0,1,insufficient_data,N/A,N/A
```
**Sample Output File 2: `output/analysis_report.txt`**
```
==================================================
Session ID    : FIT-2026-004
Participant ID: P001
Usable samples: 6/6
Classification: recovering
Rationale     : Heart rate indicates moderate activity (61.17% of max HR). Significant decline in heart rate detected towards session end.
==================================================
Session ID    : FIT-2026-005
Participant ID: P002
Usable samples: 0/5
Classification: insufficient_data
Rationale     : More than 50% of sensor readings were invalid or poor quality.
==================================================
```
**Sample Output File 2: `output/rejected_records.txt`**
```
=====================================================
              REJECTED CSV RECORDS LOG:              
=====================================================

[fitness_sessions.csv: Row 26] Field biometrics rejected: Sensor reading failed range or quality rules.
[fitness_sessions_invalid.csv: Row 3] Field biometrics rejected: Type conversion failed: could not convert string to float: 'fast'
[fitness_sessions_invalid.csv: Row 12] Field biometrics rejected: Type conversion failed: float() argument must be a string or a real number, not 'NoneType'
```

## 9. Scenario Coverage
The test suite in ```tests.py```validates five distinct operational scenarios supplied via ```data_generator.py```:
1. **Resting Session**: Low activity level and HR near baseline.
2. **Moderate Activity**: Sustained excercise at 55-74% relative HR.
3. **High Activity**: Intensive exercise at >= 75% relative HR.
4. **Activity Followed by Recovery**: Exertion phase followed by a sharp drop in HR/activity near session termination.
5. **Poor-Quality / Invalid Sensor Data**: Streams dominated by corrupted or out-of-bounds readings resulting in an ```insufficient_data``` output.

## 10. Known Limitations
- In-memory operations: Data is processed in-memory without persistent storage or database integration.
- Simulated inputs: Uses simulated batch observations generated by ```data_generator.py``` rather than real-time Bluetooth streaming inputs.
- Standard library: Metric calculations rely on standard Python arithmetic without external statistical modeling libraries like ```numpy``` or ```scipy```.
