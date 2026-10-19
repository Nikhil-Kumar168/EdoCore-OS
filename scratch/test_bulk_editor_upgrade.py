import json
import os
import subprocess
import sys

INDEX_HTML_PATH = os.path.abspath(r"c:\Users\hamra\OneDrive\Documents\Nikhil - Documents\Web Development\Projects\EdoCore OS\index.html")
SCRATCH_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_HARNESS_PATH = os.path.join(SCRATCH_DIR, "bulk_editor_upgrade_harness.html")
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
    html_content = f.read()

test_script = """
<script>
window.__TEST_LOGS = [];
function testAssert(desc, condition) {
  window.__TEST_LOGS.push({ desc: desc, pass: Boolean(condition) });
}

window.addEventListener('DOMContentLoaded', () => {
  try {
    // Check 1: Constants
    testAssert("QUESTION_TYPES contains 'Matrix Match'", Array.isArray(QUESTION_TYPES) && QUESTION_TYPES.includes('Matrix Match'));
    testAssert("QUESTION_DIFFICULTIES contains Easy, Medium, Hard", QUESTION_DIFFICULTIES.includes('Easy') && QUESTION_DIFFICULTIES.includes('Medium') && QUESTION_DIFFICULTIES.includes('Hard'));

    // Check 2: HTML select in question-form-modal
    const qTypeSelect = document.getElementById('question-input-type');
    const options = Array.from(qTypeSelect.options).map(o => o.value);
    testAssert("question-input-type has 'Matrix Match' option", options.includes('Matrix Match'));

    // Check 3: Normalization preserves Matrix Match
    const rawState = {
      tests: [{
        id: 'test-norm-1',
        title: 'Normalization Test',
        testType: 'JEE Advanced Mock',
        testDate: '2026-10-20',
        totalQuestions: 2,
        maximumMarks: 8,
        markingScheme: { correctMarks: 4, negativeMarks: 1, partialMarks: 0, unattemptedMarks: 0 },
        questions: [{
          id: 'test-norm-1-q1',
          questionNumber: '1',
          subject: 'physics',
          questionType: 'Matrix Match',
          difficulty: 'Hard',
          status: 'Correct',
          maxMarks: 4,
          marksAwarded: 3,
          timeSpentMinutes: 4.5
        }]
      }]
    };
    const norm = normalizeAppState(rawState);
    const nq = norm.tests[0].questions[0];
    testAssert("normalizeAppState keeps questionType 'Matrix Match'", nq.questionType === 'Matrix Match');
    testAssert("normalizeAppState keeps custom marksAwarded 3", nq.marksAwarded === 3);
    testAssert("normalizeAppState keeps difficulty 'Hard'", nq.difficulty === 'Hard');
    testAssert("normalizeAppState keeps timeSpentMinutes 4.5", nq.timeSpentMinutes === 4.5);

    // Setup active test in appState for Bulk Grid tests
    appState = createDefaultAppState();
    const test1 = {
      id: 'test-bulk-full',
      title: 'Full Advanced Mock 1',
      testType: 'JEE Advanced Mock',
      testDate: '2026-10-20',
      totalQuestions: 4,
      maximumMarks: 16,
      markingScheme: { correctMarks: 4, negativeMarks: 1, partialMarks: 1, unattemptedMarks: 0 },
      subjects: ['physics', 'chemistry', 'maths'],
      status: 'Planned',
      percentile: null,
      questions: [
        {
          id: 'tb-q1',
          questionNumber: '1',
          subject: 'physics',
          questionType: 'Single correct',
          difficulty: 'Medium',
          status: 'Correct',
          maxMarks: 4,
          marksAwarded: null,
          timeSpentMinutes: 2,
          topic: 'Kinematics',
          chapter: 'Kinematics',
          mistakeCategory: '',
          notes: 'Standard problem',
          userAnswer: 'A',
          correctAnswer: 'A',
          questionText: 'A particle moves with speed v...'
        },
        {
          id: 'tb-q2',
          questionNumber: '2',
          subject: 'chemistry',
          questionType: 'Matrix Match',
          difficulty: 'Hard',
          status: 'Partially Correct',
          maxMarks: 4,
          marksAwarded: 2.5,
          timeSpentMinutes: 5,
          topic: 'Coordination Compounds',
          chapter: 'Coordination Compounds',
          mistakeCategory: '',
          notes: 'Partial matching',
          userAnswer: 'P->1, Q->2',
          correctAnswer: 'P->1, Q->2, R->3',
          questionText: 'Match List I with List II'
        }
      ]
    };
    appState.tests = [test1];
    saveAppState(false);

    // Open Bulk Modal
    openBulkEntryModal(test1.id);

    testAssert("bulkWorkingQuestions has 4 rows", bulkWorkingQuestions.length === 4);
    testAssert("bulkWorkingQuestions Q1 has questionType 'Single correct'", bulkWorkingQuestions[0].questionType === 'Single correct');
    testAssert("bulkWorkingQuestions Q1 has questionText preserved", bulkWorkingQuestions[0].questionText.includes('particle'));
    testAssert("bulkWorkingQuestions Q2 has questionType 'Matrix Match'", bulkWorkingQuestions[1].questionType === 'Matrix Match');
    testAssert("bulkWorkingQuestions Q2 has custom marksAwarded 2.5", bulkWorkingQuestions[1].marksAwarded === 2.5);
    testAssert("bulkWorkingQuestions Q2 has timeSpentMinutes 5", bulkWorkingQuestions[1].timeSpentMinutes === 5);
    testAssert("Padded Q3 has status 'Unattempted'", bulkWorkingQuestions[2].status === 'Unattempted');
    testAssert("Padded Q3 has questionType 'Single correct'", bulkWorkingQuestions[2].questionType === 'Single correct');
    testAssert("Padded Q3 has maxMarks 4", bulkWorkingQuestions[2].maxMarks === 4);

    // Render Grid and verify DOM controls
    renderBulkGrid();
    const tbody = document.getElementById('bulk-grid-tbody');
    testAssert("bulk-grid-tbody rendered", tbody && tbody.children.length > 0);

    // Verify row detail toggle
    const toggleBtn1 = document.getElementById('bulk-grid-toggle-btn-0');
    testAssert("toggleBtn1 has blue accent for populated details", toggleBtn1.classList.contains('text-blue-300'));
    toggleBulkRowDetail(0);
    const detailRow0 = document.getElementById('bulk-grid-detail-0');
    testAssert("detailRow0 is visible after toggle", detailRow0 && !detailRow0.classList.contains('hidden'));

    // Edit fields in working questions via helpers
    updateBulkQuestionType(2, 'Matrix Match');
    testAssert("Q3 questionType updated to Matrix Match", bulkWorkingQuestions[2].questionType === 'Matrix Match');

    updateBulkQuestionDifficulty(2, 'Hard');
    testAssert("Q3 difficulty updated to Hard", bulkWorkingQuestions[2].difficulty === 'Hard');

    updateBulkQuestionMaxMarks(2, 6);
    testAssert("Q3 maxMarks updated to 6", bulkWorkingQuestions[2].maxMarks === 6);

    updateBulkQuestionMarksAwarded(2, 0);
    testAssert("Q3 marksAwarded explicitly set to 0", bulkWorkingQuestions[2].marksAwarded === 0);

    updateBulkQuestionMarksAwarded(0, 3.5);
    testAssert("Q1 custom marksAwarded updated to 3.5", bulkWorkingQuestions[0].marksAwarded === 3.5);

    updateBulkQuestionTime(0, 3);
    testAssert("Q1 time spent updated to 3", bulkWorkingQuestions[0].timeSpentMinutes === 3);

    updateBulkQuestionUserAnswer(2, 'A->R, B->S');
    testAssert("Q3 userAnswer updated", bulkWorkingQuestions[2].userAnswer === 'A->R, B->S');

    updateBulkQuestionCorrectAnswer(2, 'A->R, B->P');
    testAssert("Q3 correctAnswer updated", bulkWorkingQuestions[2].correctAnswer === 'A->R, B->P');

    // Blank question statement and answers are completely optional
    updateBulkQuestionText(3, '');
    updateBulkQuestionUserAnswer(3, '');
    updateBulkQuestionCorrectAnswer(3, '');
    setBulkQuestionStatus(3, 'Incorrect');
    updateBulkQuestionMistake(3, 'Conceptual Gap');
    updateBulkQuestionTopic(3, 'Thermodynamics');

    // Verify live KPI score reflects custom marks:
    // Q1: 3.5 (custom)
    // Q2: 2.5 (custom)
    // Q3: 0 (custom)
    // Q4: Incorrect, no custom marks -> -negativeMarks (-1)
    // Total score = 3.5 + 2.5 + 0 - 1 = 5.0
    updateBulkLiveKPIs();
    const scoreKpi = document.getElementById('bulk-kpi-score').textContent;
    testAssert("Live KPI score reflects custom marks: 5 / 16", scoreKpi === '5 / 16');

    // Commit results
    commitBulkResults();

    const savedTest = getTestById(test1.id);
    testAssert("Saved test has 4 questions", savedTest.questions.length === 4);
    const sq1 = savedTest.questions[0];
    const sq2 = savedTest.questions[1];
    const sq3 = savedTest.questions[2];
    const sq4 = savedTest.questions[3];

    testAssert("sq1 has marksAwarded 3.5", sq1.marksAwarded === 3.5);
    testAssert("sq1 has timeSpentMinutes 3", sq1.timeSpentMinutes === 3);
    testAssert("sq1 questionText preserved without erasing", sq1.questionText.includes('particle'));
    testAssert("sq2 has questionType 'Matrix Match'", sq2.questionType === 'Matrix Match');
    testAssert("sq2 has marksAwarded 2.5", sq2.marksAwarded === 2.5);
    testAssert("sq3 has questionType 'Matrix Match'", sq3.questionType === 'Matrix Match');
    testAssert("sq3 has difficulty 'Hard'", sq3.difficulty === 'Hard');
    testAssert("sq3 has maxMarks 6", sq3.maxMarks === 6);
    testAssert("sq3 has marksAwarded 0 (preserved)", sq3.marksAwarded === 0);
    testAssert("sq3 has userAnswer 'A->R, B->S'", sq3.userAnswer === 'A->R, B->S');
    testAssert("sq4 saved successfully with blank statement/answers", sq4.questionText === '' && sq4.userAnswer === '');
    testAssert("sq4 has mistakeCategory 'Conceptual Gap'", sq4.mistakeCategory === 'Conceptual Gap');

    // Check mistake notebook entry for sq4
    const mistake4 = (appState.mistakes || []).find(m => m.linkedTestId === test1.id && String(m.questionNumber) === '4');
    testAssert("Mistake notebook created entry for sq4", Boolean(mistake4));
    testAssert("Mistake notebook has correct category", mistake4 && mistake4.category === 'Conceptual Gap');

    // Test Paste / Import parser with extended columns
    const pasteTsv = [
      "Q#\\tSubject\\tType\\tDifficulty\\tStatus\\tMax\\tMarks\\tTopic\\tMistake Type\\tTime\\tNotes",
      "1\\tphysics\\tSingle correct\\tMedium\\tCorrect\\t4\\t4\\tKinematics\\t\\t2\\tGood speed",
      "2\\tchemistry\\tMatrix Match\\tHard\\tCorrect\\t4\\t3\\tCoordination\\t\\t4\\t3 matched",
      "3\\tmaths\\tNumerical\\tEasy\\tIncorrect\\t4\\t-1\\tCalculus\\tCalculation / Execution\\t3\\tSign error",
      "4\\tphysics\\tMultiple correct\\tMedium\\tUnattempted\\t4\\t0\\tOptics\\t\\t0\\tLeft due to time"
    ].join("\\n");

    const parsedResult = parseBulkTestInput(pasteTsv, savedTest);
    testAssert("TSV Parser succeeds with optional metadata columns", parsedResult.success === true);
    testAssert("Parser extracted 4 questions", parsedResult.questions.length === 4);
    const pq2 = parsedResult.questions[1];
    testAssert("Parser recognized Type 'Matrix Match'", pq2.questionType === 'Matrix Match');
    testAssert("Parser recognized Marks Awarded 3", pq2.marksAwarded === 3);
    testAssert("Parser recognized Time 4", pq2.timeSpentMinutes === 4);

    // Apply paste to working questions and commit
    bulkPasteParsedData = parsedResult.questions;
    applyBulkPasteToGrid();
    commitBulkResults();

    const repavedTest = getTestById(test1.id);
    testAssert("repavedTest Q2 has Type 'Matrix Match'", repavedTest.questions[1].questionType === 'Matrix Match');
    testAssert("repavedTest Q2 has marksAwarded 3", repavedTest.questions[1].marksAwarded === 3);
    testAssert("repavedTest Q3 has mistakeCategory 'Calculation / Execution'", repavedTest.questions[2].mistakeCategory === 'Calculation / Execution');

    // Test 90-Question Mock Test Scaling
    const test90 = {
      id: 'test-90-full',
      title: 'Full JEE Main Mock 90 Qs',
      testType: 'JEE Main',
      testDate: '2026-10-20',
      totalQuestions: 90,
      maximumMarks: 300,
      markingScheme: { correctMarks: 4, negativeMarks: 1, partialMarks: 0, unattemptedMarks: 0 },
      subjects: ['physics', 'chemistry', 'maths'],
      status: 'Planned',
      questions: []
    };
    appState.tests.push(test90);
    openBulkEntryModal(test90.id);
    testAssert("90-question test creates 90 bulkWorkingQuestions", bulkWorkingQuestions.length === 90);
    renderBulkGrid();
    const rows90 = document.getElementById('bulk-grid-tbody').children;
    testAssert("90-question test renders 90 rows (180 trs including details)", rows90.length === 180);

    // Keyboard shortcut test on 90 Qs
    setBulkQuestionStatus(0, 'Correct');
    setBulkQuestionStatus(1, 'Incorrect');
    updateBulkQuestionMistake(1, 'Formula / Fact Recall');
    updateBulkQuestionMarksAwarded(2, 3); // custom marks
    updateBulkLiveKPIs();

    const kpiTotal90 = document.getElementById('bulk-kpi-total').textContent;
    testAssert("KPI total is 90", kpiTotal90 === '90');
    const kpiCorrect90 = document.getElementById('bulk-kpi-correct').textContent;
    testAssert("KPI correct is 1", kpiCorrect90 === '1');
    const kpiWrong90 = document.getElementById('bulk-kpi-wrong').textContent;
    testAssert("KPI wrong is 1", kpiWrong90 === '1');

    commitBulkResults();
    const saved90 = getTestById(test90.id);
    testAssert("Saved 90-Q test has 90 questions", saved90.questions.length === 90);
    testAssert("Saved 90-Q test Q3 retains custom marksAwarded 3", saved90.questions[2].marksAwarded === 3);

    // Check Single Question Form optional entry
    openQuestionForm(test1.id);
    document.getElementById('question-input-number').value = '5';
    document.getElementById('question-input-subject').value = 'physics';
    document.getElementById('question-input-status').value = 'Correct';
    document.getElementById('question-input-type').value = 'Matrix Match';
    document.getElementById('question-input-answer').value = ''; // optional blank
    document.getElementById('question-input-correct').value = ''; // optional blank
    document.getElementById('question-input-text').value = ''; // optional blank
    saveQuestion({ preventDefault: () => {} });

    const updatedTestWithQ5 = getTestById(test1.id);
    const q5 = updatedTestWithQ5.questions.find(q => q.questionNumber === '5');
    testAssert("Question 5 saved without mandatory statement or answer", Boolean(q5));
    testAssert("Question 5 has questionType 'Matrix Match'", q5 && q5.questionType === 'Matrix Match');

    // Storage Key and Schema intact
    testAssert("STORAGE_KEY is JEE_STUDY_OS_STATE", STORAGE_KEY === 'JEE_STUDY_OS_STATE');
    testAssert("CURRENT_SCHEMA_VERSION is 11.1.0", CURRENT_SCHEMA_VERSION === '11.1.0');

    window.__TEST_READY = true;
  } catch (err) {
    window.__TEST_LOGS.push({ desc: "FATAL ERROR: " + err.message + "\\n" + err.stack, pass: false });
    window.__TEST_READY = true;
  }
});
</script>
"""

harness = html_content.replace("</body>", f"{test_script}\n</body>")
with open(TEST_HARNESS_PATH, "w", encoding="utf-8") as f:
    f.write(harness)

print(f"Wrote test harness to: {TEST_HARNESS_PATH}")
print("Launching Edge headless...")

cmd = [
    EDGE_PATH,
    "--headless",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    "--dump-dom",
    f"file:///{TEST_HARNESS_PATH.replace(os.sep, '/')}"
]

res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
print(f"Edge return code: {res.returncode}")

import re
matches = re.findall(r'window\.__TEST_LOGS\s*=\s*(\[.*?\]);', res.stdout, re.DOTALL)
if not matches:
    # Try finding via a simpler regex
    matches = re.findall(r'(\{"desc":.*?"pass":(?:true|false)\})', res.stdout)
    if matches:
        logs = [json.loads(m) for m in matches]
    else:
        print("Could not find test logs in output. Inspecting snippet:")
        print(res.stdout[-2000:])
        sys.exit(1)
else:
    logs = json.loads(matches[0])

passed = sum(1 for l in logs if l["pass"])
failed = sum(1 for l in logs if not l["pass"])
total = len(logs)

print(f"\n=======================================================")
print(f"BULK EDITOR UPGRADE: {passed}/{total} CHECKS PASSED")
print(f"=======================================================\n")

for i, l in enumerate(logs, 1):
    status = "PASS" if l["pass"] else "FAIL"
    print(f"[{status}] #{i}: {l['desc']}")

if failed > 0:
    print(f"\nFAILED: {failed} checks failed.")
    sys.exit(1)
else:
    print("\nALL BULK EDITOR UPGRADE VERIFICATION CHECKS PASSED PERFECTLY!")

