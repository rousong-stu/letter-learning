/**
 * @description 单角色管理员模式下恒定放行，保留函数签名以兼容指令和路由守卫
 */
export function hasPermission(_targetRoleOrPermission: string[] | GuardType) {
    return true
}
