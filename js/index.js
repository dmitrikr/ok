const hamburger = document.querySelector(".hamburger")
const nav_menu = document.querySelector(".nav-menu")

hamburger.addEventListener("click",()=>{
  hamburger.classList.toggle("active");
  nav_menu.classList.toggle("active");
})



fetch('https://olgaku.art/g')
.then(function (response) {
    return response.json();
}).then(function(data) {
  console.log(data)
  data.push({'name':'press','src':'press'})
  data.push({'name':'contact','src':''})
  for (var d in data) {
    li = document.createElement('li')
    li.className = 'nav-item'
    a = document.createElement('div')
    a.className = 'nav-link'
    //a.setAttribute('data', "src: '"+data[d]['src']+"'")
    a.dataset.src = data[d]['src']
    a.dataset.name = data[d]['name']
    
    a.innerText = data[d]['name'].toUpperCase()
    li.appendChild(a)
    nav_menu.appendChild(li)
    console.log(d)
  }

  li = document.createElement('li')
  li.className = 'nav-item'

  mg = document.createElement('img')
  mg.src = "icon/mg.png"
  mg.style.width = "30px"
  mg.addEventListener("click", (el) => {
    document.getElementById('searchInput').classList.toggle("active");
  })
  mg.id = 'searchIcon'
  
  a = document.createElement('input')
  a.id = 'searchInput'
  dv = document.createElement('div')
  dv.id = 'searchOutput'

  a.addEventListener("keyup", (el) => {
    fetch('https://olgaku.art/s/'+el.target.value)
    .then(function (response) {
        return response.json();
    }).then(function(data) {
      h = ''
      for (var d in data) {
        p = data[d]['thumb'].replace('i/','').replaceAll(' ', '_')
        h += '<a href="https://olgaku.art/#lg='+p+'&slide='+data[d]['slide']+'"><img src="https://olgaku.art/'+data[d]['thumb']+'/p"> '+data[d]['name']+'</a><br>'
      }
      dv.innerHTML = h
      console.log(data)
    })
  })
  a.addEventListener("focusout", (el) => {
    setTimeout(()=>{
      dv.innerHTML = ''
      el.target.value = ''
    },500)
  })
  li.appendChild(mg)
  li.appendChild(a)
  li.appendChild(dv)
  nav_menu.appendChild(li)

  document.querySelectorAll(".nav-link").forEach(n => n.addEventListener("click", (el) => {
    path = el.currentTarget.dataset.name.replaceAll(" ","_")
    history.pushState({path:path}, el.currentTarget.dataset.name, '/#'+path)
    menuItemClick(el.currentTarget)

  }))
  setNavState()
})


function getParam(param, url) {
    param = "?"+param.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + param + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    console.log(results)
    if (!results) return null;
    if (!results[2]) return '';
    return results[2].replace(/\+/g, " ");
}


function setNavState(hash){
  var hash = window.location.hash.substring(1);

  console.log(hash)
  if (hash.substring(0,3) == 'lg=') {
    hash = getParam('lg', decodeURIComponent(hash))
  } else {

  }
  console.log(hash.substring(0,3))
  sh = hash.split('/')
  cur = sh[0] 
  if (cur=='') {
    cur = "FASHION_WEEKS"
  }
  cur2 = ''
  if (sh.length>1) {
    cur2 = sh[1]
    if (cur2.indexOf(':')>0) {
      cur2s = cur2.split(':')
      cur2 = cur2s[1]
    }
  }  
  document.querySelectorAll(".nav-link").forEach((el) => {
    console.log(cur,el.dataset.name.replaceAll(" ","_"))
    if (el.dataset.name.replaceAll(" ","_")==cur) {
      console.log(cur,cur2)
      if (cur2=='') {
        menuItemClick(el)
      } else {
        activateMenuItem(el)
        fetch(el.dataset.src)
          .then(function (response) {
            return response.json();
          }).then(function(data) {
            el = document.querySelector("#gallery-dynamic-thumbnails")
            el.innerHTML = ''
            el = document.querySelector('#gallery-header')
            el.innerText = ''
            el = document.querySelector("#gal")
            el.innerHTML = ''
            for (var d in data) {
              if (data[d]['name'].toUpperCase().replaceAll(" ","_")==cur2) {
                console.log("xxx "+cur2)
                galleryClick(data[d]['src'], data[d]['name'].toUpperCase(), hash)
              }
            }
          })
      }
      console.log(el)
    }
  })
}

function activateMenuItem(el) {
  hamburger.classList.remove("active");
  nav_menu.classList.remove("active");
  document.querySelectorAll(".nav-link").forEach(div => {
    div.classList.remove("active");
  })
  ct = document.querySelector("#contact-info")
  pr = document.querySelector("#press")
  ct.style.display = 'none';
  pr.style.display = 'none';
  el.classList.add("active")

  if (el.dataset.src=="press") {
    el = document.querySelector("#gallery-dynamic-thumbnails")
    el.innerHTML = ''
    el = document.querySelector('#gallery-header')
    el.innerText = ''
    el = document.querySelector("#gal")
    el.innerHTML = ''
    pr.style.display = 'block';
    return
  }

  if (el.dataset.src=="") {
    el = document.querySelector("#gallery-dynamic-thumbnails")
    el.innerHTML = ''
    el = document.querySelector('#gallery-header')
    el.innerText = ''
    el = document.querySelector("#gal")
    el.innerHTML = ''
    ct.style.display = 'block';
    return
  }
}

function menuItemClick(el) {
  activateMenuItem(el)
  fetch(el.dataset.src)
    .then(function (response) {
      return response.json();
    }).then(function(data) {
      console.log(data)
      el = document.querySelector("#gallery-dynamic-thumbnails")
      el.innerHTML = ''
      el = document.querySelector('#gallery-header')
      el.innerText = ''
      el = document.querySelector("#gal")
      el.innerHTML = ''
      
      for (var d in data) {
        //if (data[d]['name'].contans('.jpg')) {
          i = document.createElement('img')
          //i.className = 'img-responsive'
          i.src = data[d]['img'].replace("\/b","\/p")
          div = document.createElement('figure')
          div.className = 'snip'

          a = document.createElement('figcaption')
          a.className = 'gal-link2'
          a.dataset.src = data[d]['src']
          a.dataset.caption = data[d]['name'].toUpperCase()
          
          d2 = document.createElement('div')
          p = document.createElement('p')
          p.innerText = data[d]['name'].toUpperCase()
          d2.appendChild(p)
          a.appendChild(d2)
          div.appendChild(i)
          div.appendChild(a)
          el.appendChild(div)
       // }
      }
      document.querySelectorAll(".gal-link2").forEach(n => n.addEventListener("click", (el) => {
        path = window.location.hash.substring(1)+'/'+el.currentTarget.dataset.caption.replaceAll(" ","_")
        history.pushState({path:path}, el.currentTarget.dataset.caption, '/#'+path)
        galleryClick(el.currentTarget.dataset.src, el.currentTarget.dataset.caption, path)
      }))
    })
}

function galleryClick (src, cpt, path){
  fetch(src)
    .then(function (response) {
      return response.json();
    }).then(function(data) {
      console.log(data)
      el = document.querySelector("#gal")
      el.innerHTML = ''
      el = document.querySelector('#gallery-header')
      el.innerText = cpt
      el = document.querySelector("#gallery-dynamic-thumbnails")
      el.innerHTML = ''
      for (var d in data) {
        if (data[d]['name'].includes('.jpg')) {
          a = document.createElement('a')
          a.className = 'gallery-item'
          a.setAttribute('data-src', data[d]['src']+"/b")
          //a.setAttribute('data-lg-size', "900-1600")
          a.setAttribute('data-sub-html', '<div>download</div>')

          i = document.createElement('img')
          i.className = 'img-responsive'
          i.src = data[d]['src']+"/p"
          last_src = data[d]['src']+"/p"
          a.appendChild(i)
          //a.innerText = data[d]['name'].toUpperCase()
          el.appendChild(a)
        }
      }
      for (i=0;i<5;i++){
        a = document.createElement('div')
        a.className = 'gallery-mock'
        ie = document.createElement('img')
        ie.src = last_src
        ie.className = 'img-responsive'
        a.appendChild(ie)
        el.appendChild(a)
      }

      gel = document.getElementById("gallery-dynamic-thumbnails")
      gel.addEventListener("lgAfterOpen", ()=> {
        console.log('lgAfterSlide fired')

        bbId = "lg-buy"
        bbIdMsg = "buymsg"
        tbId = "lg-toolbar-1"
        
        x = document.getElementById(bbId)
        /* t2 = document.querySelector("#lg-toolbar-2")
        if (t2 != null && x != null) {
          bbId = "lg-buy-2"
          bbIdMsg = "buymsg-2"
          x = document.getElementById(bbId)
        } */
        if (x == null) {
          console.log('lgAfterSlide need to add')
          buyIcon = document.createElement('button');
          buyIcon.type = 'button'
          buyIcon.id = bbId
          buyIcon.ariaLabel = 'Buy pic'
          buyIcon.className = 'lg-icon lg-buy'
          buyIcon.addEventListener("click",()=>{
            //xel = document.querySelector("#lg-toolbar-1")
            lnk = buyIcon.parentElement.querySelector('a').href.replace('\/i\/','/buy/')
            lnk = lnk.substring(0, lnk.length - 2);
            
            fetch(lnk, {
                method: 'get'
            }).then(res => res.json())
            .then(res => {
              buyMsg = document.getElementById(bbIdMsg)
               console.log(res)
               if (res['result']=='success') {
                  console.log('SUCCESS')
                  buyMsg.innerHTML = 'Successfully <a href="https://disk.yandex.com/client/disk/_shared" target=_blank>copied</a>'
               } else if (res['result']=='not_authorized') {
                  console.log('not_authorized')  
                  buyMsg.innerHTML = '<a href="login.html" target=_blank>Authorize</a> to continue</a>'
               } else if (res['result']=='wrong_user') {
                  console.log('wrong_user')  
                  buyMsg.innerHTML = 'Wrong user, please contact site owner'
               }
                buyMsg.classList.remove("hidden")
                buyMsg.classList.remove("fout")
                buyMsg.classList.add("fin")
                setTimeout(function() {
                  document.getElementById(bbIdMsg).classList.add("fout");
                }, 2000);
            }).catch(function(err) {
            // Called if the server returns any errors
              console.log("Error:"+err);
              buyMsg = document.getElementById(bbIdMsg)
                  buyMsg.classList.remove("hidden")
                  buyMsg.classList.remove("fout")
                  buyMsg.classList.add("fin")
                  buyMsg.innerHTML = "Error:"+err
              
            });

          })

          document.querySelector(".lg-toolbar").appendChild(buyIcon);
          buyMsg = document.createElement('div');
          buyMsg.id = bbIdMsg
          buyMsg.innerText = " "
          buyMsg.className = 'buymsg hidden'
          document.querySelector(".lg-toolbar").appendChild(buyMsg);
        }

         
      })

      try {
        //const plugin = lightGallery();
        //plugin.destroy();
        el = document.querySelector(".lg-container")
        el.remove()
      } catch (e) {

      }

      const dynamicGallery = window.lightGallery(gel, {
        dynamic: false,
        thumbnail: true,
        galleryId: path,
        subHtmlSelectorRelative: false,
        selector:'.gallery-item',
        fullScreen: true,
        plugins: [lgZoom, lgFullscreen, lgHash]
      });

  })
}

window.addEventListener('popstate', function(e){
  //self.loadImage(e.state.path, e.state.note);
  
  setNavState()
  //setNavState(e.state.path)
  /*if (e.state.type=='menu') {
    document.querySelectorAll(".nav-link").forEach((el) => {
      if (e.state.src == el.dataset.src) {
        menuItemClick(el)
      }
    })
  } else {
    // .gal-link2
    galleryClick(e.state.src, e.state.caption)

  }*/
}, false);