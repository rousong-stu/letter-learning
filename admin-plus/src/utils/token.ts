import cookie from 'js-cookie'
import { storage, tokenTableName } from '@/config'

/**
 * @description 获取token
 * @returns {string|ActiveX.IXMLDOMNode|Promise<any>|any|IDBRequest<any>|MediaKeyStatus|FormDataEntryValue|Function|Promise<Credential | null>}
 */
export function getToken() {
    if (storage) {
        switch (storage) {
            case 'localStorage': {
                return localStorage.getItem(tokenTableName)
            }
            case 'sessionStorage': {
                return sessionStorage.getItem(tokenTableName)
            }
            case 'cookie': {
                return cookie.get(tokenTableName)
            }
            default: {
                return localStorage.getItem(tokenTableName)
            }
        }
    } else {
        return localStorage.getItem(tokenTableName)
    }
}

/**
 * @description 存储token
 * @param token
 * @returns {void|*}
 */
export function setToken(token: string) {
    if (storage) {
        switch (storage) {
            case 'localStorage': {
                return localStorage.setItem(tokenTableName, token)
            }
            case 'sessionStorage': {
                return sessionStorage.setItem(tokenTableName, token)
            }
            case 'cookie': {
                return cookie.set(tokenTableName, token)
            }
            default: {
                return localStorage.setItem(tokenTableName, token)
            }
        }
    } else {
        return localStorage.setItem(tokenTableName, token)
    }
}

/**
 * @description 移除token
 * @returns {void|Promise<void>}
 */
export function removeToken() {
    if (storage) {
        switch (storage) {
            case 'localStorage': {
                return localStorage.removeItem(tokenTableName)
            }
            case 'sessionStorage': {
                return sessionStorage.clear()
            }
            case 'cookie': {
                return cookie.remove(tokenTableName)
            }
            default: {
                return localStorage.removeItem(tokenTableName)
            }
        }
    } else {
        return localStorage.removeItem(tokenTableName)
    }
}
