from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
import os, json
import shutil, re, sys
import yadisk
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import requests
from math import floor
import asyncio

__CPATH__ = '../ok_data'

app = FastAPI()
#token = 'y0_AgAAAAAA-mmVAAtL9QAAAAD7G-TcAAAT0uRCcg9Mo7_PdTjvUGt0mdNX4w'
token = 'y0_AgAAAAAAFB_iAAtPjQAAAAD7dzKvAAAXCLIGVgBAyZab6_ax4svZR5180w'

@app.get("/", response_class=HTMLResponse)
async def root():
    with open('index.html') as f:
        lines = ''.join(f.readlines())
    return lines

@app.get("/clear_all")
async def clear_all():
    return
    shutil.rmtree(__CPATH__)
    os.makedirs(__CPATH__)

@app.get("/clear")
async def clear():
    return
    dir_name = __CPATH__
    test = os.listdir(dir_name)
    for item in test:
        if item.endswith(".json"):
            os.remove(os.path.join(dir_name, item))

def sortFunc(e):
    if 'fname' in e:
        return e['fname']
    else:
        return e['name']

@app.get("/g")
@app.get("/g/{gallery}")
@app.get("/g/{gallery}/{subgallery}")
async def read_gallery(gallery="", subgallery="", force: int = 0):
    ret = []
    path = ""
    file_name = "root"
    if gallery!="":
        path += "/"+gallery
        file_name = gallery
    if subgallery!="":
        path += "/"+subgallery
        file_name += "_"+subgallery
    file_name = file_name.replace(" ","-")
    file_path = __CPATH__+"/"+file_name+".json"
    #print(file_path)
    if os.path.exists(file_path) and force==0:
        #print('use cache')
        with open(file_path, "r") as f:
            ret = json.loads(f.read())
        #print(ret)
    else:
        client = yadisk.Client(token=token)
        print(client.check_token())
        with client:
            #print(client.check_token())

            for res in client.listdir("/_portfolio"+path, preview_size="600x900"):
                if res.name=="cover.jpg":
                    a=1
                elif ".jpg" in res.path:
                    pt = res.path.replace("disk:/_portfolio","i").replace(".jpg","")
                    ret.append({"name":res.name, "src":pt,"thumb":pt}) #,"subHtml":res.name,"subHtmlUrl":""})
                elif res.type=="dir":
                    pt = res.path.replace("disk:/_portfolio","g")
                    pti = res.path.replace("disk:/_portfolio","i")+"/cover/b"
                    n = res.name.split('__')
                    ret.append({"fname":res.name, "name":n[-1], "path":res.name, "src":pt, "img":pti}) #,"subHtml":res.name,"subHtmlUrl":""})
                #print(n[-1], res.path)
                #print(res)
        ret.sort(reverse=True, key=sortFunc)
        with open(file_path, 'w') as f:
            json.dump(ret, f)
    return ret

@app.get("/s/{term}")
async def search_gallery(term=""):
    ret = []
    if term == '':
        return ret
    files = [f for f in os.listdir(__CPATH__+"/") if os.path.isfile(__CPATH__+"/"+f)]
    regex = r"(.*)"+term+"(.*)"
    pattern = re.compile(regex)
    maxItems = 10
    i = 0
    for f in files:
        if f[-4:] == 'json':
            cnt=0
            with open(__CPATH__+"/"+f, "r") as f:
                d = json.loads(f.read())
                for p in d:
                    fnd = re.findall(pattern, p['name'])
                    if len(fnd) > 0:
                        p['slide'] = cnt
                        ret.append(p)
                        i+=1
                        if i>=maxItems:
                            return ret
                    cnt+=1
    return ret


@app.get("/i/{gallery}/{subgallery}/{image}/{size}")
async def read_img2(gallery, subgallery, image, size):
    image+=".jpg"
    dir_path = __CPATH__+"/f/"+gallery+"/"+subgallery
    dir_path_b = __CPATH__+"/b/"+gallery+"/"+subgallery
    dir_path_p = __CPATH__+"/p/"+gallery+"/"+subgallery
    
    dir_path_def = dir_path_p

    do_reload = True
    if size=="br":
        size="b"
        do_reload = True
    if size=="bf":
        size="b"
        #todo delete
        if os.path.exists(dir_path+"/"+image):
            os.remove(dir_path+"/"+image)
        if os.path.exists(dir_path_b+"/"+image):
            os.remove(dir_path_b+"/"+image)
        if os.path.exists(dir_path_p+"/"+image):
            os.remove(dir_path_p+"/"+image)
    if size=="b":
        dir_path_def = dir_path_b
    
    os.makedirs(dir_path, exist_ok=True)
    os.makedirs(dir_path_p, exist_ok=True)
    os.makedirs(dir_path_b, exist_ok=True)
    #print('start')
    
    if image=='cover.jpg' and os.path.exists(dir_path_p+"/"+image) and os.path.getsize(dir_path_p+"/"+image)==0:
        return FileResponse('./cover.jpg', filename=image)
    elif os.path.exists(dir_path_def+"/"+image) and os.path.getsize(dir_path_def+"/"+image)>0:
        #print(dir_path_def+"/"+image, os.path.getsize(dir_path_def+"/"+image))
        #if os.path.exists(dir_path+"/"+image):
        #    os.remove(dir_path+"/"+image)
        return FileResponse(dir_path_def+"/"+image, filename=image)
    else:
        if not do_reload:
            return FileResponse('./cover.jpg', filename='image.jpg')
        print("RELOAD ", dir_path+"/"+image) #, os.path.getsize(dir_path+"/"+image))
        if not os.path.exists(dir_path+"/"+image) or os.path.getsize(dir_path+"/"+image)<1000:
            client = yadisk.Client(token=token)
            print("TRY download", "/_portfolio/"+gallery+"/"+subgallery+"/"+image)
            if True:
                try:
                    client.download("/_portfolio/"+gallery+"/"+subgallery+"/"+image, dir_path+"/"+image)
                    file_size = os.path.getsize(dir_path+"/"+image)

                    print('download finish', file_size)
                    if file_size<1000:
                        return False
                except:
                    dir_path = '.'
                    image = 'cover.jpg'
                    return FileResponse('./cover.jpg', filename=image)
            else:
                client.download("/_portfolio/"+gallery+"/"+subgallery+"/"+image, dir_path+"/"+image)


        size = 1200, 1900
        wmsize = 1000
        try:
            if not os.path.exists(dir_path+"/"+image) or os.path.getsize(dir_path+"/"+image)==0:
                print("File not exists")
                raise ValueError( "File not exists")
            im = Image.open(dir_path+"/"+image)
            im.thumbnail(size, Image.Resampling.LANCZOS)
        except:
            try:
                client = yadisk.Client(token=token)
                client.download("/_portfolio/"+gallery+"/"+subgallery+"/"+image, dir_path+"/"+image)
                im = Image.open(dir_path+"/"+image)
                im.thumbnail(size, Image.Resampling.LANCZOS)
            except:
                return False

        
        
        im2 = im.convert("RGBA")

        txt = Image.new("RGBA", im.size, (255, 255, 255, 0))
        imw = Image.open('watermark.jpg')
        w, h = imw.size
        imw.thumbnail((wmsize,floor(h*(wmsize/w))), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(imw)
        w1, h1 = im.size
        w, h = imw.size
        x, y = int(w / 2), int(h / 2)
        if x > y:
          font_size = y
        elif y > x:
          font_size = x
        else:
          font_size = x
        font = ImageFont.truetype("league.ttf", int(font_size/2))
        font2 = ImageFont.truetype("league.ttf", int(font_size/2))
        #draw.text((x, y-font_size/2.4), "https://olgaku.art", fill=(255, 255, 255, 130), font=font, anchor='ms')
        #draw.text((x, y), "OlgaKu", fill=(255, 255, 255, 130), font=font2, anchor='ms')
        #draw.text((x, y+font_size/3), "@olgakulyova", fill=(255, 255, 255, 130), font=font, anchor='ms')
    
        al = 225 
        y = int(y*1.1)
        font_size = int(font_size * 0.9)
        draw.text((x, y-font_size/1.6), "https://olgaku.art", fill=(255, 255, 255, al), font=font, anchor='ms')
        draw.text((x, y), "OlgaKu", fill=(255, 255, 255, al), font=font2, anchor='ms')
        draw.text((x, y+font_size/1.6), "@olgakulyova", fill=(255, 255, 255,  al), font=font, anchor='ms')
        al = 165
        imw.putalpha(al)
        txt.paste(imw, (w1-w,floor(h1*0.6),w1,floor(h1*0.6)+h))
        im = Image.alpha_composite(im2, txt).convert("RGB")
        im.save(dir_path_b+"/"+image, "JPEG", subsampling=0, quality=90)

        im = Image.open(dir_path+"/"+image)
        size = 1200, 600
        im.thumbnail(size, Image.Resampling.LANCZOS)
        im.save(dir_path_p+"/"+image, "JPEG", subsampling=0, quality=95)
        if os.path.exists(dir_path+"/"+image):       
            os.remove(dir_path+"/"+image)

        #client.download("/_portfolio/"+gallery+"/"+subgallery+"/"+image, dir_path+"/"+image)
    print(dir_path_def+"/"+image)
    return FileResponse(dir_path_def+"/"+image, filename=image)


@app.get("/i2/{gallery}/{subgallery}/{image}/{size}")
async def read_img(gallery, subgallery, image, size):
    return False
    image+=".jpg"
    sz=""
    if size=="p":
        sz = "600x900"
    elif size=="b":
        sz = "1600x2600"
    else:
        size = "f"
    dir_path = __CPATH__+"/"+size+"/"+gallery+"/"+subgallery
    os.makedirs(dir_path, exist_ok=True)
    if not os.path.exists(dir_path+"/"+image):
        client = yadisk.Client(token=token)
        try:
            mt = client.get_meta("/_portfolio/"+gallery+"/"+subgallery+"/"+image, preview_size=sz)
            #os.unlink(dir_path+"/"+image)
            #print(mt.preview)
            client.download_by_link(mt.preview, dir_path+"/"+image)
        except:
            dir_path = "."
            image = 'cover.jpg'

        #client.download("/_portfolio/"+gallery+"/"+subgallery+"/"+image, dir_path+"/"+image)
    print(dir_path+"/"+image)
    return FileResponse(dir_path+"/"+image)


@app.get("/buy/{gallery}/{subgallery}/{image}")
async def buy_img(gallery, subgallery, image, request: Request):
    
    user_email = 'eprodcontentcreative@yandex.ru'
    user_email2 = 'dmitrikr@yandex.ru'
    url = "https://login.yandex.ru/info?format=json"
    t = request.cookies.get('x-auth')
    if t==None:
        return {"result":"not_authorized"}
    r = requests.get(url, headers={"Authorization":"OAuth "+t})
    print(r.json())
    res = r.json()
    print('email', res['default_email'])
    if res['default_email'] == user_email  or res['default_email'] == user_email2:
        client = yadisk.Client(token=token)
        print('BUY', "/_portfolio/"+gallery+"/"+subgallery+"/"+image+".jpg", "/_shared/"+gallery+" "+subgallery+" "+image+".jpg")
        client.copy("/_portfolio/"+gallery+"/"+subgallery+"/"+image+".jpg", "/_shared/"+gallery+" "+subgallery+" "+image+".jpg", overwrite=True)
        return {"result":"success"}
    else:
        return {"result":"wrong_user"}
    #return r.json()


@app.get("/auth/callback")
async def auth_callback(request: Request):
    token = request.headers.get('X-Auth')
    print('X-Auth', token)

    if token!='':
        user_email = 'eprodcontentcreative@yandex.ru'
        user_email2 = 'dmitrikr@yandex.ru'
        url = "https://login.yandex.ru/info?format=json"
        r = requests.get(url, headers={"Authorization":"OAuth "+token})
        if r.status_code==401:
            print("auth not_authorized")
            return {"result":"not_authorized"}
        else:
            print('auth', r.status_code)
            res = r.json()
            print('auth', res['default_email'])
            if res['default_email'] == user_email or res['default_email'] == user_email2:
                print('auth success')
                return {"result":"success"}
            else:
                print('auth wrong_user ')
                return {"result":"wrong_user"}
    return {"result":"not_authorized"}

if __name__ == "__main__":

    if len(sys.argv)==1:
        l1, l2, l3 = 0, 0, 0
        if False:
            gals = asyncio.run(read_gallery())
            
            for gg in gals:
                l1+=1
                print(gg["path"])
                subgals = asyncio.run(read_gallery(gg["path"]))
                for g in subgals:
                    l2+=1
                    print(gg["path"], g["path"])
                    imgs = asyncio.run(read_gallery(gg["path"], g["path"]))
                    for im in imgs:
                        l3+=1
                        #break


        gals = asyncio.run(read_gallery())
        ll1, ll2, ll3 = 0, 0, 0
        for gg in gals:
            ll1+=1
            if True: #gg["path"] == 'FASHION':
                subgals = asyncio.run(read_gallery(gg["path"]))
                for g in subgals:
                    ll2+=1
                    print(gg["path"], g["path"])
                    imgs = asyncio.run(read_gallery(gg["path"], g["path"]))
                    #print(ll3, "/", l3, gg["path"], g["path"], "cover")
                    #i = asyncio.run(read_img2(gg["path"], g["path"], "cover", "b"))

                    for im in imgs:
                        ll3+=1
                        #print(im["name"])
                        #if im["name"]=="cover.jpg": #gg["path"] == 'FASHION':
                        print(ll3, "/", l3, gg["path"], g["path"], im["name"])
                        i = asyncio.run(read_img2(gg["path"], g["path"], im["name"].replace(".jpg",""), "br"))
                            
                    #break
            #print("----",gg)
            #print(subgals)
    elif sys.argv[1] == 'rename':
        client = yadisk.Client(token=token)
        gals = asyncio.run(read_gallery(force=1))
        l1, l2, l3 = 0, 0, 0
        for gg in gals:
            l1+=1
            print(gg["path"])
            subgals = asyncio.run(read_gallery(gg["path"],force=1))
            for g in subgals:
                l2+=1
                print(gg["path"], g["path"])
                if ":" in g["path"]:
                    print('rename', gg["path"], g["path"])
                    l3+=1
                    client.rename("/_portfolio/"+gg["path"]+'/'+g["path"], g["path"].replace(":", "__"))
    elif sys.argv[1] == 'cover':
        print(FileResponse('./cover.jpg'))

    elif sys.argv[1] == 'test':
        gallery="FASHION WEEKS"
        subgallery="202603:SHANGHAI FASHION WEEK AW26"
        image="cover.jpg"

        gallery="FASHION"
        subgallery="FASHION"
        image="00001.jpg"

        size="p"
        client = yadisk.Client(token=token)
        print(client.check_token())
        print(client.get_disk_info())

        for item in client.listdir("/_portfolio/FASHION WEEKS/202603:SHANGHAI FASHION WEEK AW26"):
            if item['name'] == 'cover.jpg':
                print(item['path'][5:])
                client.download(item['path'][5:].replace(':','\\:'), "cover.jpg")
                #print(item)

        #client.download("/_portfolio/"+gallery+"/"+subgallery+"/"+image, "cover.jpg")

        '''

        asyncio.run(read_img2(gallery, subgallery, image, size)) '''
    elif sys.argv[1] == 'search':
        term = "3"
        ret = []
        if term == '':
            print(ret)
        regex = r"(.*)"+term+"(.*)"
        pattern = re.compile(regex)
        maxItems = 10
        i = 0
        for f in os.listdir(__CPATH__+"/"):
            #if not os.path.isfile(f):
            #    continue
            ret.append(f)
            if f[-4:] == 'json':
                with open(__CPATH__+"/"+f, "r") as f:
                    d = json.loads(f.read())
                    for p in d:
                        fnd = re.findall(pattern, p['name'])
                        if len(fnd) > 0:
                            ret.append(p)
                            i+=1
                            if i>=maxItems:
                                print(ret)


