const recordBtn = document.querySelector(".record-btn");
const inputArea = document.getElementById("inputArea");
const popup = document.getElementById("popup");
const symptomtext = document.getElementById("symptomtext");
const slider = document.getElementById("myRange");
const sendMessage = document.getElementById("sendMessage");
const recorder = document.getElementById("recorder");
const nowQuestion = document.getElementById("nowQuestion");
const lastQuestion = document.getElementById("lastQuestion");

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function openPopup(text) {
  symptomtext.innerHTML = text;
  sendMessage.setAttribute("disabled","disabled");
  recorder.setAttribute("disabled","disabled");
  inputArea.setAttribute("disabled","disabled");
  popup.classList.add("open_popup");
}

function closePopup() {
  app.getSliderValue();
  slider.value = "2";
  if (nowQuestion.value != "end"){
    sendMessage.removeAttribute("disabled");
    recorder.removeAttribute("disabled");
    inputArea.removeAttribute("disabled"); 
  }
  popup.classList.remove("open_popup");
}


if (navigator.mediaDevices.getUserMedia) {
  var chunks = [];
  const constraints = { audio: true };
  navigator.mediaDevices.getUserMedia(constraints).then(
    stream => {
      console.log("授權成功!");

      const mediaRecorder = new MediaRecorder(stream, { mimeType: "video/webm;codecs=vp9" });

      recordBtn.onclick = () => {
        if (mediaRecorder.state === "recording") {
          mediaRecorder.stop();
          recordBtn.textContent = "record";
          recordBtn.blur();
          inputArea.focus();
          console.log("錄音結束");
        } else {
          if (app.audio.duration > 0 && !app.audio.paused){
            app.audio.pause();
          }
          mediaRecorder.start();
          console.log("錄音中...");
          recordBtn.textContent = "stop";
        }
        console.log("錄音狀態：", mediaRecorder.state);
      };

      mediaRecorder.ondataavailable = e => {
        chunks.push(e.data);
      };

      mediaRecorder.onstop = e => {
        var blob = new Blob(chunks);
        let formData = new FormData();
        formData.append('data',blob);
        // console.log('blob',blob);
        $.ajax({
            type: "POST",
            url: "/result",
            data: formData,
            dataType: "text",
            contentType: false,
            processData: false
        }).done(function (response){
          var result  = JSON.parse(response);
          console.log(result.stt);
          inputArea.value = result.stt;
          app.input_message = result.stt;
          chunks = [];
        })
        
      };
    },
    () => {
      console.error("授權失敗！");
    }
  );
} else {
  console.error("不支持 getUserMedia");
}