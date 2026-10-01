// Guide pages: build the "On this page" list from h2/h3 headings (kramdown gives them ids).
(function () {
  var content = document.getElementById("guide-content");
  var list = document.getElementById("toc-list");
  if (!content || !list) return;
  var heads = content.querySelectorAll("h2[id], h3[id]");
  if (heads.length < 2) return;
  heads.forEach(function (h) {
    var li = document.createElement("li");
    if (h.tagName === "H3") li.className = "sub";
    var a = document.createElement("a");
    a.href = "#" + h.id;
    a.textContent = h.textContent;
    li.appendChild(a);
    list.appendChild(li);
  });
  list.closest(".toc").hidden = false;

  if (!("IntersectionObserver" in window)) return;
  var links = list.querySelectorAll("a");
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      links.forEach(function (l) {
        l.classList.toggle("active", l.getAttribute("href") === "#" + e.target.id);
      });
    });
  }, { rootMargin: "-80px 0px -70% 0px" });
  heads.forEach(function (h) { io.observe(h); });
})();

// Copy buttons on code blocks.
(function () {
  if (!navigator.clipboard) return;
  document.querySelectorAll(".prose div.highlighter-rouge, .prose figure.highlight").forEach(function (block) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "copy-btn";
    btn.textContent = "Copy";
    btn.addEventListener("click", function () {
      var code = block.querySelector("pre code") || block.querySelector("pre");
      navigator.clipboard.writeText(code.innerText).then(function () {
        btn.textContent = "Copied";
        setTimeout(function () { btn.textContent = "Copy"; }, 1500);
      });
    });
    block.appendChild(btn);
  });
})();

// Jobs: hide listings that expired since the last build, and filter by tag.
(function () {
  var list = document.getElementById("job-list");
  var today = new Date().toISOString().slice(0, 10);
  document.querySelectorAll(".job[data-expires]").forEach(function (job) {
    if (job.dataset.expires < today) job.remove();
  });
  if (!list) return;
  var empty = document.getElementById("jobs-empty");
  var jobs = list.querySelectorAll(".job");
  if (empty) empty.hidden = jobs.length > 0;
  var buttons = document.querySelectorAll(".filter button");
  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var tag = btn.dataset.tag;
      buttons.forEach(function (b) { b.classList.toggle("active", b === btn); });
      jobs.forEach(function (job) {
        job.hidden = tag && job.dataset.tags.split(",").indexOf(tag) === -1;
      });
    });
  });
})();
