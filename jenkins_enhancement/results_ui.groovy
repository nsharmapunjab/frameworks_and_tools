pattern = ~/^.*\b("NEW-TC|NEW-TC)\b.*$/
def map = [:]
manager.build.logFile.eachLine { line ->
matcher = pattern.matcher(line)
if(matcher.matches()) {
       ownClass = matcher.group(0)
        sunClass = matcher.group(1)
        map[ownClass] = sunClass
}
}
if(map.size() > 0) {
   summary = manager.createSummary("notepad.png")
   summary.appendText("NEWLY ADDED TEST CASES !!!!", false, true, false, "black")
   map.each{ k, v -> summary.appendText("${k}", false) }
summary.appendText("", false)
}

pattern2 = ~/^.*\b("DEL-TC|DEL-TC)\b.*$/
def map2 = [:]
manager.build.logFile.eachLine { line ->
matcher2 = pattern2.matcher(line)
if(matcher2.matches()) {
       ownClass = matcher2.group(0)
        sunClass = matcher2.group(1)
        map2[ownClass] = sunClass
}
}
if(map2.size() > 0) {
   summary2 = manager.createSummary("notepad.png")
   summary2.appendText("DELETED TEST CASES !!!!", false, true, false, "black")
   map2.each{ k, v -> summary2.appendText("${k}", false) }
summary2.appendText("", false)
}

