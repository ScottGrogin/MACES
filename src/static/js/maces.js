async function init(username, password) {
  const headers = new Headers();
  headers.append("Content-Type", "application/json");
  const data = JSON.stringify({
    username: username,
    password: password,
  });

  const requestOptions = {
    method: "POST",
    headers: headers,
    body: data,
    redirect: "follow",
  };

  const loginResult = await fetch("/login", requestOptions);
  if (loginResult.status != 200) {
    const response = await loginResult.json();
    throw new Error(response.message);
  }
  const isOfficerResult = await fetch("/is_park_officer");
  if (isOfficerResult.status != 200) {
    throw new Error("Could not determine officer status");
  }
  const officerData = await isOfficerResult.json();
  return {
    isOfficer: officerData.isOfficer,
    parkId: officerData.parkId,
  };
}

async function getClasses() {
  const response = await fetch("/get_classes");
  const data = await response.json();
  data.sort((a, b) => a.class_id - b.class_id);
  return data;
}

function setClassOptions(classData) {
  const selectElement = document.getElementById("classSelect");
  classData.forEach((element) => {
    let option = document.createElement("option");
    option.value = element.class_id;
    option.innerHTML = element.class_name;
    selectElement.appendChild(option);
  });
}

async function writeAttendance(
  classId,
  className,
  hostParkId,
  date,
  attending_in_person,
  event_calendar_detail_id = 0
) {
  const headers = new Headers();
  headers.append("Content-Type", "application/json");

  const data = JSON.stringify({
    class_id: classId,
    class_name: className,
    host_park_id: hostParkId,
    date: date,
    submitted: false,
    attending_in_person: attending_in_person,
    event_calendar_detail_id: event_calendar_detail_id,
  });
  const requestOptions = {
    method: "POST",
    headers: headers,
    body: data,
    redirect: "follow",
  };
  const attendanceResponse = await fetch("/attendance", requestOptions);
  const attendanceData = await attendanceResponse.json();
  return attendanceData;
}

async function submitAttendance(
  host_park_id,
  date,
  credit_data,
  event_calendar_detail_id = 0
) {
  const headers = new Headers();
  headers.append("Content-Type", "application/json");

  const data = JSON.stringify({
    host_park_id: host_park_id,
    date: date,
    submitted: false,
    credit_data,
    event_calendar_detail_id: event_calendar_detail_id,
  });
  const requestOptions = {
    method: "POST",
    headers: headers,
    body: data,
    redirect: "follow",
  };
  const attendanceResponse = await fetch("/submit_attendance", requestOptions);
  const attendanceData = await attendanceResponse.json();
  return attendanceData;
}
