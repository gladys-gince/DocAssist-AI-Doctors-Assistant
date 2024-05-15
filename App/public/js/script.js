const audioContext = new (window.AudioContext || window.webkitAudioContext)();

// Variables to store recording state and recorder
let isRecording = false;
let recorder;

const navBar = document.querySelector("nav"),
  menuBtns = document.querySelectorAll(".menu-icon"),
  overlay = document.querySelector(".overlay");

menuBtns.forEach((menuBtn) => {
  menuBtn.addEventListener("click", () => {
    navBar.classList.toggle("open");
  });
});

overlay.addEventListener("click", () => {
  navBar.classList.remove("open");
});

const appointment_form = document.getElementById("appointment_form");

function toggleModal() {
  var overlay = document.getElementsByClassName("overlay")[0];

  if (overlay.style.display === "block") {
    overlay.style.display = "none";
    appointment_form.style.display = "none";
  } else {
    overlay.style.display = "block";
    appointment_form.style.display = "block";
  }
}

function submitForm() {
  var form = document.getElementById("appointmentForm");
  var formData = new FormData(form);

  fetch("/book_appointment", {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      if (data["msg"] == "received") {
        overlay.style.display = "none";
        appointment_form.style.display = "none";
        document.getElementById("confirmation-msg").style.display = "block";
        setTimeout(() => {
          document.getElementById("confirmation-msg").style.display = "none";
          location.reload();
        }, 5000);
      }
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
    });
}

function hide_form() {
  var overlay = document.getElementsByClassName("overlay")[0];
  overlay.style.display = "none";
  appointment_form.style.display = "none";
}

var user_id = 0;
var appointment_id = 0;
let mediaRecorder;
let audioChunks = [];

document.addEventListener("click", function (event) {
  var target = event.target;

  // Check if the clicked element has the class "stop-btn"
  if ($(target).hasClass("stop-btn")) {
    stopRecording();
    $(target)
      .closest("tr")
      .find(".pause-btn, .resume-btn")
      .closest("td")
      .remove();

    // Replace the "Stop" button with a "Done" button
    $(target).removeClass("stop-btn").addClass("done-btn").text("Done");
  }

  // Check if the clicked element has the class "start_button"
  if (target.classList.contains("start_button")) {
    startRecording();
    var rowData = $(target)
      .closest("tr")
      .find("td")
      .map(function () {
        return $(this).text();
      })
      .get();
    user_id = rowData[2];
    appointment_id = rowData[1];
    var row = $(target).closest("tr");
    row.append('<td><button class="pause-btn">Pause</button></td>');
    $(target).removeClass("start_button").addClass("stop-btn").text("Stop");
  }

  // Check if the clicked element has the class "pause-btn"
  if ($(target).hasClass("pause-btn")) {
    // Your logic for the "Pause" button
    pauseRecording();
    // Toggle the class and text content
    $(target).toggleClass("pause-btn resume-btn").text("Resume");
  }

  else if ($(target).hasClass("resume-btn")) {
    resumeRecording();
    $(target).toggleClass("resume-btn pause-btn").text("Pause");
  }
});


async function startRecording() {

    document.getElementById('patient_profile').style.display = 'block';

  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);

  mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) {
      audioChunks.push(event.data);
    }
  };

  mediaRecorder.onstop = () => {

    document.getElementById('patient_profile').style.display = 'none';
    // When recording is stopped, send the recorded audio to the server
    const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
    additionalData = {
        'user_id' : user_id,
        'appointment_id' : appointment_id
    }
    // Send the recorded audio to the server
    const formData = new FormData();
    formData.append("audio", audioBlob);
    for (var key in additionalData) {
      formData.append(key, additionalData[key]);
    }
    fetch("/recording", {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (response.ok) {
          console.log("Recording sent successfully");
        } else {
          console.error("Failed to send recording");
        }
      })
      .catch((error) => {
        console.error("Error sending recording:", error);
      });

    // Reset audioChunks
    audioChunks = [];
  };

  mediaRecorder.start();
}

function pauseRecording() {
  mediaRecorder.pause();
}

function resumeRecording() {
  mediaRecorder.resume();
}

function stopRecording() {
  mediaRecorder.stop();
}
