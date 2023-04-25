const recordBtn = document.querySelector(".record-btn");
const inputArea = document.getElementById("inputArea");

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
          console.log("錄音結束");
        } else {
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
  console.error("浏览器不支持 getUserMedia");
}