import xml.etree.ElementTree as ET
import re
import os
import time

WHOLE=r"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-export SYSTEM "http://xml.evernote.com/pub/evernote-export2.dtd">
<en-export export-date="20181012T102525Z" application="Evernote/Windows" version="6.x">
%(allnotes)s
</en-export>
"""
NOTE=r"""<note>
        <title>%(title)s</title>
        <content>
<![CDATA[<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">
<en-note>%(content)s</en-note>]]>
        </content>
        <created>%(created)s</created>
        <note-attributes>
            <author>yeahbeen@163.com</author>
        </note-attributes>
    </note>
"""
notes = ""

for name in os.listdir('Notes'):
            file = os.path.join('Notes', name,"Info")
            print(file)

            with open(file,mode="rb") as f:
                allstr = f.read()
                try:
                    allstr = allstr.decode(encoding="utf_16_le")
                except Exception as e:
                    print("Exception")
                    print(e)
                    matchObj = re.match('^.*in position (\d+)', str(e), re.M)
                    if matchObj:
                        print("matchObj")
                        print(matchObj.group(1))
                        allstr = allstr[:int(matchObj.group(1))].decode(encoding="utf_16_le")
                matchObj = re.match('^(.*)\.note', allstr[2:], re.M)
                title = matchObj.group(1)
                print(title)
            file = os.path.join('Notes', name,"Content")
            # print(file)
            with open(file,mode="r",encoding="utf_16_le") as f:
                allstr = f.read()
                raw = allstr[2:].replace("\xa0","\x20")
                content = ""
                if '<?xml version="1.0"?>' not in raw:
                    content = "<div>"+raw+"</div>"
                    content = re.sub("<img .*\/>", "", content)
                else:
                    try:
                        root = ET.fromstring(raw)
                        for ele in root.iter():
                            # print(ele)
                            if ele.tag == '{http://note.youdao.com}para':
                                t = ele.find('{http://note.youdao.com}text')
                                if t.text is None:
                                    text = ""
                                else:
                                    text = t.text
                                # print(t.text)        
                                print(text)
                                if re.match("<img .*\/>",text):
                                    text = ""                                
                                text = text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                                content += "<div>"+text+"</div>"
                                coid = ele.find('{http://note.youdao.com}coId')
                                if coid.text is not None:
                                    matchObj = re.match('^\d{4}-(\d{10})\d{3}', coid.text)
                                    if matchObj:
                                        timestruct = time.gmtime(int(matchObj.group(1)))
                                        ctime = time.strftime('%Y%m%dT%H%M%SZ', timestruct)
                                        print(ctime)
                    except Exception as e:
                        print(e)
                        content = "<div>"+raw+"</div>"
                        content = re.sub("<img .*\/>", "", content)
                print(content)
            note = NOTE % dict(title = title,content = content,created = ctime)
            print(note)
            notes += note + "\n"
            
whole = WHOLE % dict(allnotes = notes)
whole = whole.encode(encoding="utf8").decode(encoding="utf8").replace("<br>","<br/>")
with open("save.enex","w") as f:
    f.write(whole)