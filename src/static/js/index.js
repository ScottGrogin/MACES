let userParkId = null;

function getHostParkId() {
  const params = new URLSearchParams(window.location.search);
  return params.get("parkId");
}

function getEventDate() {
  const params = new URLSearchParams(window.location.search);
  return params.get("date");
}

async function handleLogin(event) {
  event.preventDefault(); // stop form reload

  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;
  log("Logging in...");
  try {
    const result = await init(username, password);
    const isOfficer = result.isOfficer;
    userParkId = result.parkId;
    log("Login successful!");
    const classData = await getClasses();
    setClassOptions(classData);
    manageDisplay(userParkId, isOfficer);
  } catch (err) {
    console.error(err);
    log("Login failed: " + err.message);
  }
}

function manageDisplay(userParkId, isOfficer) {
  const _hostParkId = getHostParkId();
  const _date = getEventDate();
  const paramsArePopulated = _hostParkId && _date;
  const isOfficerForThisPark = isOfficer && userParkId == _hostParkId;
  const lut = {
    officerSetup: ["parkDateSelection"],
    officerReady: ["classSection", "adminOptions"],
    playerReady: ["classSection"],
  };
  // Hide all sections first
  ["loginFormDiv", "classSection", "parkDateSelection", "adminOptions"].forEach(
    (id) => {
      document.getElementById(id).style.display = "none";
    }
  );

  // Get display key from helper function
  const key = getDisplayKey(
    isOfficer,
    isOfficerForThisPark,
    paramsArePopulated
  );
  if (!key) return;

  // Show only relevant sections
  lut[key].forEach((id) => {
    document.getElementById(id).style.display = "block";
  });
}

function getDisplayKey(isOfficer, isOfficerForThisPark, paramsArePopulated) {
  if (isOfficer && !paramsArePopulated) return "officerSetup";
  if (isOfficerForThisPark && paramsArePopulated) return "officerReady";
  if (!isOfficerForThisPark && paramsArePopulated) return "playerReady";
  return null;
}

async function submitClass(event) {
  event.preventDefault();

  const selectedClass = document.getElementById("classSelect");
  const selectedClassId = selectedClass.value;
  const selectedClassName =
    selectedClass.options[selectedClass.selectedIndex].text;
  const attendingInPerson = document.querySelector(
    'input[name="attending"]:checked'
  )?.value;

  const params = new URLSearchParams(window.location.search);
  const parkId = params.get("parkId");
  const date = params.get("date");
  log("Submitting class...");
  const response = await writeAttendance(
    selectedClassId,
    selectedClassName,
    parkId,
    date,
    attendingInPerson
  );
  log(response.message);
}

async function submitCredits(e) {
  e.preventDefault();

  const inputs = document.querySelectorAll(
    "#creditSubmissionForm input[type='number']"
  );
  const creditData = {};

  inputs.forEach((input) => {
    const key = input.dataset.label;
    creditData[key] = Number(input.value);
  });

  const params = new URLSearchParams(window.location.search);
  const parkId = params.get("parkId");
  const date = params.get("date");
  log("Submitting credits to ORK...");
  const response = await submitAttendance(parkId, date, creditData);
  log(response.message);
}

function generateUrl(e) {
  e.preventDefault();
  const creditDate = document.getElementById("parkDate").value;
  const baseUrl = window.location.origin;
  log("Generating url");
  document.getElementById(
    "generatedUrl"
  ).textContent = `${baseUrl}?parkId=${userParkId}&date=${creditDate}`;
}

window.addEventListener("DOMContentLoaded", () => {
  document.getElementById("loginForm").addEventListener("submit", handleLogin);
  document.getElementById("classForm").addEventListener("submit", submitClass);
  document.getElementById("dateForm").addEventListener("submit", generateUrl);
  document
    .getElementById("creditSubmissionForm")
    .addEventListener("submit", submitCredits);
});
