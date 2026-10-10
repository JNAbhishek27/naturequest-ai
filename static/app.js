/**
 * NatureQuest AI — Frontend Controller
 * Touch Grass Challenge — Distraction-free, resilient, client-stateful application
 */

document.addEventListener('DOMContentLoaded', () => {
  // Navigation & Sections
  const modelStatusBadge = document.getElementById('model-status-badge');
  const modelStatusText = document.getElementById('model-status-text');

  const generatorSection = document.getElementById('generator-section');
  const briefingSection = document.getElementById('briefing-section');
  const outdoorSection = document.getElementById('outdoor-section');
  const reflectionSection = document.getElementById('reflection-section');

  // Form Controls
  const missionForm = document.getElementById('mission-form');
  const submitMissionBtn = document.getElementById('submit-mission-btn');
  const btnText = submitMissionBtn.querySelector('.btn-text');
  const btnLoader = submitMissionBtn.querySelector('.btn-loader');
  const formErrorAlert = document.getElementById('form-error-alert');

  // Briefing Controls
  const backToEditBtn = document.getElementById('back-to-edit-btn');
  const missionOriginTag = document.getElementById('mission-origin-tag');
  const briefingTitle = document.getElementById('briefing-title');
  const briefingTime = document.getElementById('briefing-time');
  const briefingTaskCount = document.getElementById('briefing-task-count');
  const briefingEnvTag = document.getElementById('briefing-env-tag');
  const briefingDescription = document.getElementById('briefing-description');
  const briefingLowScreen = document.getElementById('briefing-low-screen');
  const briefingTasksList = document.getElementById('briefing-tasks-list');
  const briefingTipsList = document.getElementById('briefing-tips-list');
  const briefingSafetyList = document.getElementById('briefing-safety-list');
  const headingOutsideBtn = document.getElementById('heading-outside-btn');

  // Outdoor Mode Controls
  const exitOutdoorBtn = document.getElementById('exit-outdoor-btn');
  const outdoorProgressText = document.getElementById('outdoor-progress-text');
  const outdoorProgressPercent = document.getElementById('outdoor-progress-percent');
  const outdoorProgressBar = document.getElementById('outdoor-progress-bar');
  const activeTaskBadge = document.getElementById('active-task-badge');
  const activeTaskText = document.getElementById('active-task-text');
  const taskCompletedCheckbox = document.getElementById('task-completed-checkbox');
  const checkboxActionText = document.getElementById('checkbox-action-text');
  const prevTaskBtn = document.getElementById('prev-task-btn');
  const nextTaskBtn = document.getElementById('next-task-btn');
  const finishMissionBtn = document.getElementById('finish-mission-btn');

  // Reflection Controls
  const statsTasksCompleted = document.getElementById('stats-tasks-completed');
  const statsDuration = document.getElementById('stats-duration');
  const reflectionQuestionDisplay = document.getElementById('reflection-question-display');
  const fieldNotesTextarea = document.getElementById('field-notes');
  const saveNoteBtn = document.getElementById('save-note-btn');
  const noteSavedIndicator = document.getElementById('note-saved-indicator');
  const startNewMissionBtn = document.getElementById('start-new-mission-btn');

  // State
  let currentMission = null;
  let activeTaskIndex = 0;
  let completedTasksSet = new Set();
  const STORAGE_KEY_MISSION = 'naturequest_active_mission';
  const STORAGE_KEY_PROGRESS = 'naturequest_task_progress';
  const STORAGE_KEY_NOTES = 'naturequest_field_notes';

  // -------------------------------------------------------------------------
  // 1. Initial Model Status Check
  // -------------------------------------------------------------------------
  async function checkModelStatus() {
    try {
      const res = await fetch('/api/model-status');
      if (!res.ok) throw new Error('Status endpoint failed');
      const data = await res.json();

      if (data.configured) {
        modelStatusBadge.className = 'status-badge';
        modelStatusText.textContent = `Gemma (${data.model_id})`;
        modelStatusBadge.title = 'AI is configured and ready to generate custom missions.';
      } else {
        modelStatusBadge.className = 'status-badge fallback';
        modelStatusText.textContent = 'Gemma Ready (Sample Fallback Mode)';
        modelStatusBadge.title = 'No live API key found. Using structured offline sample missions.';
      }
    } catch (err) {
      modelStatusBadge.className = 'status-badge fallback';
      modelStatusText.textContent = 'Engine Offline (Using Sample Missions)';
    }
  }
  checkModelStatus();

  // -------------------------------------------------------------------------
  // 2. Mission Generation Request
  // -------------------------------------------------------------------------
  missionForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    formErrorAlert.classList.add('hidden');
    formErrorAlert.textContent = '';

    const formData = new FormData(missionForm);
    const interests = formData.getAll('interests');

    if (interests.length === 0) {
      showFormError('Please select at least one nature interest to focus on.');
      return;
    }

    const payload = {
      environment: formData.get('environment'),
      time_minutes: parseInt(formData.get('time_minutes'), 10),
      difficulty: formData.get('difficulty'),
      interests: interests,
      instruction: (formData.get('instruction') || '').trim()
    };

    setLoading(true);

    try {
      const resp = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await resp.json();

      if (!resp.ok || !result.success) {
        throw new Error(result.error || 'Failed to generate mission.');
      }

      currentMission = result.mission;
      currentMission._userEnvironment = payload.environment;
      activeTaskIndex = 0;
      completedTasksSet.clear();

      // Persist to local storage
      saveCurrentMissionLocally();

      renderBriefing(currentMission);
      showSection(briefingSection);
      window.scrollTo({ top: briefingSection.offsetTop - 80, behavior: 'smooth' });

    } catch (err) {
      showFormError(err.message || 'Network error occurred. Please check connection and try again.');
    } finally {
      setLoading(false);
    }
  });

  function showFormError(msg) {
    formErrorAlert.textContent = msg;
    formErrorAlert.classList.remove('hidden');
  }

  function setLoading(loading) {
    submitMissionBtn.disabled = loading;
    if (loading) {
      btnText.classList.add('hidden');
      btnLoader.classList.remove('hidden');
    } else {
      btnText.classList.remove('hidden');
      btnLoader.classList.add('hidden');
    }
  }

  // -------------------------------------------------------------------------
  // 3. Render Mission Briefing
  // -------------------------------------------------------------------------
  function renderBriefing(mission) {
    briefingTitle.textContent = mission.mission_title;
    briefingTime.textContent = mission.estimated_minutes;
    briefingTaskCount.textContent = mission.three_to_five_tasks.length;
    briefingEnvTag.textContent = (mission._userEnvironment || 'Local Spot').toUpperCase();
    briefingDescription.textContent = mission.mission_description;
    briefingLowScreen.textContent = mission.low_screen_mode_instruction;

    if (mission.is_sample_fallback) {
      missionOriginTag.className = 'origin-tag fallback-tag';
      missionOriginTag.textContent = 'Structured Sample Mission (Live Key Absent)';
      missionOriginTag.title = mission.fallback_reason || '';
    } else {
      missionOriginTag.className = 'origin-tag';
      missionOriginTag.textContent = `Generated by ${mission.model_engine || 'Gemma'}`;
    }

    // Tasks list preview
    briefingTasksList.innerHTML = '';
    mission.three_to_five_tasks.forEach((task) => {
      const li = document.createElement('li');
      li.textContent = task;
      briefingTasksList.appendChild(li);
    });

    // Tips list
    briefingTipsList.innerHTML = '';
    (mission.observation_tips || []).forEach((tip) => {
      const li = document.createElement('li');
      li.textContent = tip;
      briefingTipsList.appendChild(li);
    });

    // Safety list
    briefingSafetyList.innerHTML = '';
    (mission.safety_reminders || []).forEach((safety) => {
      const li = document.createElement('li');
      li.textContent = safety;
      briefingSafetyList.appendChild(li);
    });
  }

  backToEditBtn.addEventListener('click', () => {
    showSection(generatorSection);
  });

  headingOutsideBtn.addEventListener('click', () => {
    startOutdoorMode();
  });

  // -------------------------------------------------------------------------
  // 4. Outdoor Mode (Distraction-Free Field Flow)
  // -------------------------------------------------------------------------
  function startOutdoorMode() {
    if (!currentMission) return;
    showSection(outdoorSection);
    renderOutdoorTask();
    window.scrollTo({ top: outdoorSection.offsetTop - 40, behavior: 'smooth' });
  }

  function renderOutdoorTask() {
    const total = currentMission.three_to_five_tasks.length;
    const taskText = currentMission.three_to_five_tasks[activeTaskIndex];

    activeTaskBadge.textContent = `Task ${activeTaskIndex + 1} of ${total}`;
    activeTaskText.textContent = taskText;

    // Is current task done?
    const isCompleted = completedTasksSet.has(activeTaskIndex);
    taskCompletedCheckbox.checked = isCompleted;
    updateCheckboxLabel(isCompleted);

    // Prev / Next button states
    prevTaskBtn.disabled = activeTaskIndex === 0;
    nextTaskBtn.disabled = activeTaskIndex === total - 1;

    // Progress updates
    const completedCount = completedTasksSet.size;
    const percent = Math.round((completedCount / total) * 100);
    outdoorProgressText.textContent = `Task ${activeTaskIndex + 1} of ${total} (${completedCount} completed)`;
    outdoorProgressPercent.textContent = `${percent}%`;
    outdoorProgressBar.style.width = `${percent}%`;

    // Completion button visibility
    if (completedCount === total) {
      finishMissionBtn.classList.remove('hidden');
    } else {
      finishMissionBtn.classList.add('hidden');
    }
  }

  function updateCheckboxLabel(isCompleted) {
    if (isCompleted) {
      checkboxActionText.textContent = '✓ Completed! Great observation.';
      checkboxActionText.style.color = '#1f3b2b';
    } else {
      checkboxActionText.textContent = 'Mark this task completed';
      checkboxActionText.style.color = '';
    }
  }

  taskCompletedCheckbox.addEventListener('change', () => {
    if (taskCompletedCheckbox.checked) {
      completedTasksSet.add(activeTaskIndex);
    } else {
      completedTasksSet.delete(activeTaskIndex);
    }
    updateCheckboxLabel(taskCompletedCheckbox.checked);
    saveProgressLocally();
    renderOutdoorTask();
  });

  prevTaskBtn.addEventListener('click', () => {
    if (activeTaskIndex > 0) {
      activeTaskIndex -= 1;
      renderOutdoorTask();
    }
  });

  nextTaskBtn.addEventListener('click', () => {
    const total = currentMission.three_to_five_tasks.length;
    if (activeTaskIndex < total - 1) {
      activeTaskIndex += 1;
      renderOutdoorTask();
    }
  });

  exitOutdoorBtn.addEventListener('click', () => {
    showSection(briefingSection);
  });

  // -------------------------------------------------------------------------
  // 5. Completion & Reflection
  // -------------------------------------------------------------------------
  finishMissionBtn.addEventListener('click', () => {
    const total = currentMission.three_to_five_tasks.length;
    statsTasksCompleted.textContent = `${completedTasksSet.size} / ${total}`;
    statsDuration.textContent = `${currentMission.estimated_minutes} min`;
    statsScreenSaved.textContent = '100% Focused';

    reflectionQuestionDisplay.textContent = `"${currentMission.one_reflection_question}"`;
    
    // Load existing note if saved
    const savedNotes = localStorage.getItem(STORAGE_KEY_NOTES) || '';
    fieldNotesTextarea.value = savedNotes;

    showSection(reflectionSection);
    window.scrollTo({ top: reflectionSection.offsetTop - 60, behavior: 'smooth' });
  });

  saveNoteBtn.addEventListener('click', () => {
    const note = fieldNotesTextarea.value.trim();
    localStorage.setItem(STORAGE_KEY_NOTES, note);
    noteSavedIndicator.classList.remove('hidden');
    setTimeout(() => {
      noteSavedIndicator.classList.add('hidden');
    }, 3000);
  });

  startNewMissionBtn.addEventListener('click', () => {
    // Clear active mission state
    localStorage.removeItem(STORAGE_KEY_MISSION);
    localStorage.removeItem(STORAGE_KEY_PROGRESS);
    currentMission = null;
    activeTaskIndex = 0;
    completedTasksSet.clear();
    showSection(generatorSection);
    window.scrollTo({ top: generatorSection.offsetTop - 60, behavior: 'smooth' });
  });

  // -------------------------------------------------------------------------
  // 6. Section Visibility Helper
  // -------------------------------------------------------------------------
  function showSection(targetSection) {
    [generatorSection, briefingSection, outdoorSection, reflectionSection].forEach((sec) => {
      if (sec === targetSection) {
        sec.classList.remove('hidden');
      } else {
        sec.classList.add('hidden');
      }
    });
  }

  // -------------------------------------------------------------------------
  // 7. Local Storage Persistence
  // -------------------------------------------------------------------------
  function saveCurrentMissionLocally() {
    try {
      localStorage.setItem(STORAGE_KEY_MISSION, JSON.stringify(currentMission));
    } catch (e) {
      // Storage quota or privacy mode
    }
  }

  function saveProgressLocally() {
    try {
      const arr = Array.from(completedTasksSet);
      localStorage.setItem(STORAGE_KEY_PROGRESS, JSON.stringify(arr));
    } catch (e) {}
  }

  function restoreSavedMissionIfAny() {
    try {
      const savedMissionRaw = localStorage.getItem(STORAGE_KEY_MISSION);
      if (!savedMissionRaw) return;

      const parsedMission = JSON.parse(savedMissionRaw);
      if (parsedMission && parsedMission.three_to_five_tasks) {
        currentMission = parsedMission;
        const progressRaw = localStorage.getItem(STORAGE_KEY_PROGRESS);
        if (progressRaw) {
          const arr = JSON.parse(progressRaw);
          completedTasksSet = new Set(arr);
        }
        renderBriefing(currentMission);
        showSection(briefingSection);
      }
    } catch (e) {
      // Ignore corrupt storage
    }
  }
  restoreSavedMissionIfAny();
});
