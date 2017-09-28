// This file is required by the index.html file and will
// be executed in the renderer process for that window.
// All of the Node.js APIs are available in this process.
const {shell} = require('electron')
const path = require('path')

var search = function () {
    $("ul li").remove();

    var keyWord = document.getElementById("keyWord").value;
    var parent = document.getElementById("paper_list");
    for (var key in papers) {
        for (var word in papers[key]["tags"]) {
            if (word.toLowerCase().indexOf(keyWord.toLowerCase()) >= 0) {
                var li = document.createElement("li");
                li.className = "list-group-item";

                var link = document.createElement("a");
                link.href = "javascript:void(0);";
                //link.url = path.join(__dirname, papers[key]["url"]);
                link.url = path.join("D:\\我的坚果云\\", papers[key]["url"]);
                link.onclick = function() {
                    shell.openItem(this.url);
                    this.style.color = '#23527c';
                    return false;
                };
                link.innerHTML = papers[key]["fileName"];

                li.appendChild(link);
                parent.appendChild(li);

                break;
            }
        }
    }
};

document.getElementById("search").addEventListener("click", search);

document.getElementById("keyWord").addEventListener("keypress", function () {
    if(event.keyCode == 13) {
        search();
    }
});
