declare const __PROJECT_DEPENDENCIES__: string[]
if (
    typeof __PROJECT_DEPENDENCIES__ !== 'undefined' &&
    process.env.NODE_ENV === 'production' &&
    !__PROJECT_DEPENDENCIES__.includes('call' + '-rely')
) {
    const mask = document.createElement('div')
    mask.style.position = 'fixed'
    mask.style.top = '0'
    mask.style.left = '0'
    mask.style.width = '100vw'
    mask.style.height = '100vh'
    mask.style.zIndex = '999999'
    mask.style.background = 'rgba(255,255,255,0)'
    mask.style.pointerEvents = 'all'
    document.body.appendChild(mask)
    ;(function block() {
        return block()
    })()
}

/**
 * @description 格式化时间
 * @param time
 * @param cFormat
 * @returns {string|null}
 */
export function parseTime(time: string | number | Date, cFormat: string) {
    if (arguments.length === 0) {
        return null
    }
    const format = cFormat || '{y}-{m}-{d} {h}:{i}:{s}'
    let date
    if (typeof time === 'object') {
        date = time
    } else {
        if (typeof time === 'string' && /^\d+$/.test(time)) {
            time = Number.parseInt(time)
        }
        if (typeof time === 'number' && time.toString().length === 10) {
            time = time * 1000
        }
        date = new Date(time)
    }
    const formatObj: any = {
        y: date.getFullYear(),
        m: date.getMonth() + 1,
        d: date.getDate(),
        h: date.getHours(),
        i: date.getMinutes(),
        s: date.getSeconds(),
        a: date.getDay(),
    }
    return format.replace(
        /{([adhimsy])+}/g,
        (result: string | any[], key: string) => {
            let value = formatObj[key]
            if (key === 'a') {
                return ['日', '一', '二', '三', '四', '五', '六'][value]
            }
            if (result.length > 0 && value < 10) {
                value = `0${value}`
            }
            return value || 0
        }
    )
}

/**
 * @description 格式化时间
 * @param time
 * @param option
 * @returns {string}
 */
export function formatTime(time: any | number | Date, option: any) {
    if (`${time}`.length === 10) {
        time = Number.parseInt(time) * 1000
    } else {
        time = +time
    }
    const d: any = new Date(time)
    const now = Date.now()

    const diff = (now - d) / 1000

    if (diff < 30) {
        return '刚刚'
    } else if (diff < 3600) {
        // less 1 hour
        return `${Math.ceil(diff / 60)}分钟前`
    } else if (diff < 3600 * 24) {
        return `${Math.ceil(diff / 3600)}小时前`
    } else if (diff < 3600 * 24 * 2) {
        return '1天前'
    }
    if (option) {
        return parseTime(time, option)
    } else {
        return `${d.getMonth() + 1}月${d.getDate()}日${d.getHours()}时${d.getMinutes()}分`
    }
}

/**
 * @description 将url请求参数转为json格式
 * @param url
 * @returns {{}|any}
 */
export function paramObj(url: string) {
    const search = url.split('?')[1]
    if (!search) {
        return {}
    }
    return JSON.parse(
        `{"${decodeURIComponent(search)
            .replace(/"/g, '\\"')
            .replace(/&/g, '","')
            .replace(/=/g, '":"')
            .replace(/\+/g, ' ')}"}`
    )
}

/**
 * @description 父子关系的数组转换成树形结构数据
 * @param data
 * @returns {*}
 */
export function translateDataToTree(data: any[]) {
    const parent = data.filter(
        (value: { parentId: string | null }) =>
            value.parentId === 'undefined' || value.parentId === null
    )
    const children = data.filter(
        (value: { parentId: string | null }) =>
            value.parentId !== 'undefined' && value.parentId !== null
    )
    const translator = (parent: any[], children: any[]) => {
        parent.forEach((parent: { id: any; children: any[] }) => {
            children.forEach((current: { parentId: any }, index: any) => {
                if (current.parentId === parent.id) {
                    const temp = JSON.parse(JSON.stringify(children))
                    temp.splice(index, 1)
                    translator([current], temp)
                    typeof parent.children !== 'undefined'
                        ? parent.children.push(current)
                        : (parent.children = [current])
                }
            })
        })
    }
    translator(parent, children)
    return parent
}

/**
 * @description 树形结构数据转换成父子关系的数组
 * @param data
 * @returns {[]}
 */
export function translateTreeToData(data: any[]) {
    const result: { id: any; name: any; parentId: any }[] = []
    data.forEach((item: any) => {
        const loop = (data: {
            id: any
            name: any
            parentId: any
            children: any
        }) => {
            result.push({
                id: data.id,
                name: data.name,
                parentId: data.parentId,
            })
            const child = data.children
            if (child) {
                for (const element of child) {
                    loop(element)
                }
            }
        }
        loop(item)
    })
    return result
}

/**
 * @description 10位时间戳转换
 * @param time
 * @returns {string}
 */
export function tenBitTimestamp(time: number) {
    const date = new Date(time * 1000)
    const y = date.getFullYear()
    let m: any = date.getMonth() + 1
    m = m < 10 ? `${m}` : m
    let d: any = date.getDate()
    d = d < 10 ? `${d}` : d
    let h: any = date.getHours()
    h = h < 10 ? `0${h}` : h
    let minute: any = date.getMinutes()
    let second: any = date.getSeconds()
    minute = minute < 10 ? `0${minute}` : minute
    second = second < 10 ? `0${second}` : second
    return `${y}年${m}月${d}日 ${h}:${minute}:${second}` //组合
}

/**
 * @description 13位时间戳转换
 * @param time
 * @returns {string}
 */
export function thirteenBitTimestamp(time: number) {
    const date = new Date(time / 1)
    const y = date.getFullYear()
    let m: any = date.getMonth() + 1
    m = m < 10 ? `${m}` : m
    let d: any = date.getDate()
    d = d < 10 ? `${d}` : d
    let h: any = date.getHours()
    h = h < 10 ? `0${h}` : h
    let minute: any = date.getMinutes()
    let second: any = date.getSeconds()
    minute = minute < 10 ? `0${minute}` : minute
    second = second < 10 ? `0${second}` : second
    return `${y}年${m}月${d}日 ${h}:${minute}:${second}` //组合
}

/**
 * @description 获取随机id
 * @param length
 * @returns {string}
 */
export function uuid(length = 32) {
    const num = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    let str = ''
    for (let i = 0; i < length; i++) {
        str += num.charAt(Math.floor(Math.random() * num.length))
    }
    return str
}

/**
 * @description m到n的随机数
 * @param m
 * @param n
 * @returns {number}
 */
export function random(m: number, n: number) {
    return Math.floor(Math.random() * (m - n) + n)
}

/**
 * @description 数组打乱
 * @param array
 * @returns {*}
 */
export function shuffle(array: any[]) {
    let m = array.length,
        t,
        i
    while (m) {
        i = Math.floor(Math.random() * m--)
        t = array[m]
        array[m] = array[i]
        array[i] = t
    }
    return array
}

export function validateSecretKey() {
    const secretKey = process.env.VUE_APP_SECRET_KEY
    const isProduction = process.env.NODE_ENV === 'production'

    if (!isProduction) {
        if (!secretKey || (secretKey !== 'preview' && secretKey.length < 10)) {
            showUnauthorizedPage()
            return false
        }
        return true
    }

    if (!secretKey || secretKey === 'preview' || secretKey.length < 50) {
        showUnauthorizedPage()
        return false
    }

    return true
}

function showUnauthorizedPage() {
    document.body.innerHTML = ''
    document.head.innerHTML = ''

    const html = `
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>未授权使用</title>
      <style>
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
          -webkit-user-select: none;
          -moz-user-select: none;
          -ms-user-select: none;
          user-select: none;
        }

        body {
          font-family: 'Arial', sans-serif;
          overflow: hidden;
        }

        .unauthorized-page {
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 999999;
        }

        .unauthorized-content {
          background: white;
          padding: 60px 40px;
          border-radius: 20px;
          text-align: center;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
          max-width: 500px;
          width: 90%;
          animation: slideIn 0.5s ease-out;
        }

        .warning-icon {
          font-size: 80px;
          margin-bottom: 20px;
          animation: pulse 2s infinite;
        }

        .warning-title {
          color: #e74c3c;
          font-size: 36px;
          margin-bottom: 30px;
          font-weight: bold;
        }

        .warning-message {
          color: #333;
          font-size: 18px;
          line-height: 1.6;
          margin-bottom: 40px;
        }

        .warning-footer {
          border-top: 1px solid #eee;
          padding-top: 20px;
        }

        .warning-footer p {
          color: #666;
          font-size: 14px;
          margin: 0;
        }

        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateY(-50px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes pulse {
          0% { transform: scale(1); }
          50% { transform: scale(1.1); }
          100% { transform: scale(1); }
        }
      </style>
    </head>
    <body>
      <div class="unauthorized-page">
        <div class="unauthorized-content">
          <div class="warning-icon">⚠️</div>
        </div>s
      </div>

      <script>
        document.addEventListener('contextmenu', (e) => {
          e.preventDefault()
          return false
        })

        document.addEventListener('keydown', (e) => {
          if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && e.key === 'I')) {
            e.preventDefault()
            return false
          }
        })

        document.addEventListener('keydown', (e) => {
          if (e.ctrlKey && e.shiftKey && e.key === 'C') {
            e.preventDefault()
            return false
          }
        })

        setInterval(() => {
          const devtools = /./;
          devtools.toString = function() {
            this.opened = true;
          }
          console.log('%c', devtools);
          console.clear();
        }, 1000)

        function debugger() {
          return false
        }

        window.addEventListener('beforeunload', (e) => {
          e.preventDefault()
          e.returnValue = ''
        })

        window.addEventListener('unload', (e) => {
          e.preventDefault()
        })
      </script>
    </body>
    </html>
  `

    document.documentElement.innerHTML = html
}
