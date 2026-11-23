# Post-Decision Evidence and Confidence Experiment

A Python/PsychoPy implementation of a perceptual decision-making experiment designed to investigate how post-decisional evidence influences confidence and subsequent choice behaviour.

## Research objective

The experiment manipulates evidence presented after an initial left/right decision. Additional dots provide evidence designed to strengthen or weaken the participant's initial choice. This manipulation is used to study confidence judgments and sequential effects in decision-making.

## Experimental design

The default configuration includes:

- One practice block with 10 trials.
- Seven main blocks with 64 trials each.
- Four difficulty levels, two target sides, and two post-decisional evidence conditions (stronger/weaker).
- Five additional dots presented after the initial response.
- A six-category confidence judgment in the final six main blocks.
- Counterbalanced ordering of confidence labels based on participant ID parity.

The task samples dot locations from bivariate normal distributions and records stimulus coordinates, decision, response time, accuracy, confidence rating, and post-decisional evidence condition.

## Requirements

Python, PsychoPy, NumPy, and pywin32 (for the Windows screen-resolution call).

```bash
pip install psychopy numpy pywin32
```

## Required instruction assets

The script expects an Instructions directory containing Slide1.JPG through Slide15.JPG. These study-specific instruction images are not included and must be supplied locally before running the task. The script checks for missing slides and reports the missing path.

## Run

1. Place the 15 instruction images in the expected Instructions directory.
2. Run the script from the project directory:

```bash
python BeehivesParadigm_2023_01.py
```

3. Enter a participant ID and the requested demographic information in the PsychoPy dialog.

The task creates a Data directory when needed and uses PsychoPy's ExperimentHandler to save participant-level trial data.

## Recorded variables

Trial records include block and trial identifiers, practice/main status, difficulty, target side, response, accuracy, response time, confidence judgment and response time, pre- and post-decisional dot coordinates and means, and the evidence-shift condition. Timed-out trials are retained with missing evidence summaries instead of causing undefined-variable errors.

## Environment and reproducibility notes

The task uses Windows-specific screen-resolution access and checks for an approximately 60 Hz display refresh rate. The measured frame time is recorded with each trial. These assumptions should be reviewed before running the task on another operating system or monitor configuration. Participant data and instruction assets are not distributed here.
