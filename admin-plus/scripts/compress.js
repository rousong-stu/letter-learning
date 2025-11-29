const fs = require('fs')
const path = require('path')
const archiver = require('archiver')

// 压缩文件名
const zipFileName = `dist.zip`
const zipFilePath = path.join(__dirname, '..', 'dist', zipFileName)

// 创建输出流
const output = fs.createWriteStream(zipFilePath)
const archive = archiver('zip', {
    zlib: { level: 9 }, // 设置压缩级别
})

// 监听错误事件
archive.on('error', (err) => {
    throw err
})

// 监听关闭事件
output.on('close', () => {
    const sizeInMB = (archive.pointer() / 1024 / 1024).toFixed(2)
    console.log(`✅ 压缩完成！`)
    console.log(`📦 文件名: ${zipFileName}`)
    console.log(`📏 文件大小: ${sizeInMB} MB`)
    console.log(`📍 文件路径: ${zipFilePath}`)
})

// 监听警告事件
archive.on('warning', (err) => {
    if (err.code === 'ENOENT') {
        console.warn('⚠️  警告:', err.message)
    } else {
        throw err
    }
})

// 管道输出
archive.pipe(output)

// 检查dist目录是否存在
const distPath = path.join(__dirname, '..', 'dist')
if (!fs.existsSync(distPath)) {
    console.error('❌ 错误: dist目录不存在，请先运行构建命令')
    process.exit(1)
}

console.log('🚀 开始压缩构建文件...')

// 递归添加dist目录内的所有文件和文件夹到压缩包根目录
function addDirectoryToArchive(dirPath, archivePath = '') {
    const items = fs.readdirSync(dirPath)

    items.forEach((item) => {
        const fullPath = path.join(dirPath, item)
        const relativePath = archivePath ? path.join(archivePath, item) : item
        const stat = fs.statSync(fullPath)

        if (stat.isDirectory()) {
            // 递归添加子目录
            addDirectoryToArchive(fullPath, relativePath)
        } else {
            // 跳过压缩包文件本身，避免自包含
            if (item !== zipFileName) {
                // 添加文件到压缩包根目录
                archive.file(fullPath, { name: relativePath })
            }
        }
    })
}

// 添加dist目录内的所有文件到压缩包根目录
addDirectoryToArchive(distPath)

// 添加package.json到压缩包（可选）
archive.file(path.join(__dirname, '..', 'package.json'), {
    name: 'package.json',
})

// 添加README.md到压缩包（如果存在）
const readmePath = path.join(__dirname, '..', 'README.md')
if (fs.existsSync(readmePath)) {
    archive.file(readmePath, { name: 'README.md' })
}

// 完成压缩
archive.finalize()
