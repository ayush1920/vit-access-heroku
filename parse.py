import re
import codecs
import json

def attendanceParse(data):
    try:
        JSONformat ={}
        data = re.findall("style=\"margin: 0px;\">(.*?)</p>",data)
        data = [{'uid':data[i+3],'value':[data[i+1],data[i+2],data[i+6],data[i+7],data[i+8]]} for i in range(0, len(data), 9)]
        JSONformat['total'] = len(data)
        JSONformat['values'] = data
        response = "OK"
        if data ==[]:
           raise ValueError('Empty data')
        return json.dumps({'attendance' : JSONformat, "response" : response})
    except:
        return 'error'
         
def routineParse(s):
    try:
        s = re.search("<table id=\"timeTableStyle\"(.*?)<\/table>",s,re.DOTALL)
        s = s.group(1)
        JSONformat = {}
        ind =0
        l,m,index = [],[],[]
        cnt,init =1,1
        day =['MON','TUE','WED','THU','FRI']
        for i in range(len(day)):
            index.append(s.find(day[i]))
        index.append(len(s))
        while(s.find("</td",ind)>0):
            ind = s.find("</td",ind)
            ind1 = ind-(40-s[ind-40:ind].find('>'))
            if(ind-ind1>10):
                l.append([cnt,s[ind1+1:ind]])
            cnt+=1
            ind=ind+150
            if ind>index[init]:
                init+=1
                m.append(l)
                l=[]
        for ind,i in enumerate(m):
            lab =[]
            theory =[]
            for j in i:
                k = j[0]%29
                if k<=15 and k>0:
                    k=k-2
                    theory.append([k,j[1]])
                if k>15:
                    k=k-16
                    lab.append([k,j[1]])
                if k==0:
                    k=13
                    theory.append([k,j[1]])
            JSONformat[day[ind]] = {'lab':lab,'theory':theory}
        return json.dumps({'routine' : JSONformat, "response" : 'OK'})
    except:
        return 'error'

def marksParse(s):
    try:
        s=s.replace('\r','').replace('\t','')
        p=s
        JSONformat = {}
        s = re.findall("tableContent-level1\">(.*?)</tr>",s,re.DOTALL)
        l =[]
        m=[]
        for i in s:
            if i[0:28]=='\n<td><output>1</output></td>':
                l.append(m)
                m=[]
            m.append(i.replace('></output>','').replace('</output>','$').replace('output','').replace('td','').replace('\n','').replace('/','').replace('<','').replace('>','')[:-1:].split('$')[:7])
        l.append(m)
        del l[0]
        # subject
        cpy=[]
        p = re.findall('<tr class=\"tableContent\" >(.*?)<\/tr>',p,re.DOTALL)
        
        for i in p:
            k = i.replace('\t','').replace('</td>\n','$').replace('<td>','').replace('\n','')[:-1:].split('$')
            cpy.append([k[0], k[2], k[3], k[6]])
        JSONformat['subdata'] = cpy
        JSONformat['marks'] = l
        return json.dumps({'marksdata' : JSONformat, 'response':'OK'})
    except:
        return 'error'
