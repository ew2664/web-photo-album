var checkout = {};
const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;
const msg = document.getElementById("msg");
const imgs = document.getElementById("imgs");
const labels = document.getElementById("labels");
const keywords = document.getElementById("keywords");
const customFile = document.getElementById("customFile");
const fileMsg = document.getElementById("fileMsg");
const uploadResult = document.getElementById("uploadResult");
const searchId = document.getElementById("searchId");

let imgsArray = [];

$(window).on("keydown", function (e) {
  if (e.which == 13 && e.target.id == "keywords") {
    searchWords();
    return false;
  }
  if (e.which == 13 && e.target.id == "labels") {
    uploadImg();
    return false;
  }
});

function speak() {
  if (SpeechRecognition !== undefined) {
    let recognition = new SpeechRecognition();

    recognition.onstart = () => {
      msg.innerHTML = "Listening...";
    };

    recognition.onspeechend = () => {
      recognition.stop();
      msg.innerHTML = "Done listening!";
    };

    recognition.onresult = (result) => {
      var res = result.results["0"]["0"]["transcript"];
      keywords.value = res;
      displayPhotos(res);
      recognition.stop();
    };

    recognition.start();

    searchId.onclick = function () {
      recognition.stop();
    };
  } else {
    console.warn("No support for speech-to-text");
  }
}

function searchWords() {
  let keywords = document.getElementById("keywords").value;
  keywords = keywords.trim();
  keywords = keywords.toLowerCase();
  displayPhotos(keywords);
}

function displayPhotos(words) {
  sdk
    .searchGet({
      q: words,
      "x-api-key": "89jZNsHr4T2nclZRBHMeb8ddhHdour8t91FNhlZM",
    })
    .then((response) => {
      imgs.innerHTML = "";
      var results = response.data.results;
      console.log(response);
      if (results && results.length > 0) {
        msg.innerHTML = "Showing your results";
        for (var r of results) {
          console.log(r);
          var img = document.createElement("img");
          img.src = r["url"];
          img.width = 100;
          img.height = 100;
          console.log(img);
          imgs.appendChild(img);
        }
      } else {
        msg.innerHTML = "No results found.";
      }
    })
    .catch((error) => {
      msg.innerHTML = "Error: " + error;
    });
}

function uploadImg() {
  var files = customFile.files;
  console.log(files);
  if (!files.length) {
    fileMsg.innerHTML = "No file has been uploaded.";
    return;
  }
  var file = files[0];
  file.constructor = () => file;
  var reader = new FileReader();
  reader.onload = function () {
    return sdk
      .uploadPut(
        {
          key: file.name,
          "Content-Type": file.type,
          "x-amz-meta-customLabels": labels.value,
          "x-api-key": "89jZNsHr4T2nclZRBHMeb8ddhHdour8t91FNhlZM",
        },
        file
      )
      .then((response) => {
        console.log(response);
        labels.value = "";
        customFile.value = "";
        uploadResult.innerHTML = "Image has been uploaded!";
      });
  };
  reader.readAsBinaryString(file);
}
