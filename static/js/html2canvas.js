$(function(){
    $("#capBtn").on("click", function(){
        var fortuneContainer = document.querySelector("#capture");
        fortuneContainer.classList.add("capture-btn-invisible");
        // 캡쳐할 영역을 html2canvas로 캡쳐하여 canvas로 변환
        setTimeout(function() {
            fortuneContainer.classList.remove("capture-btn-invisible");
            },10);
             html2canvas(document.querySelector("#capture")).then(canvas => {
                saveImg(canvas.toDataURL('image/jpg'), "dailyVS-fortune.jpg");
        });
    });

    // 캡쳐된 파일을 저장하는 함수
    function saveImg(uri, filename) {
        var link = document.createElement('a');
        if (typeof link.download === 'string') {
            link.href = uri;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            window.open(uri);
        }
    }
});
