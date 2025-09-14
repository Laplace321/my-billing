// 后端API服务
import express from 'express'
import cors from 'cors'
import fs from 'fs'
import path from 'path'

const app = express()
const PORT = 3001

// 中间件
app.use(cors())
app.use(express.json())

// 确保raw_assets目录存在
const rawAssetsDir = path.join(__dirname, '..', 'raw_assets')
if (!fs.existsSync(rawAssetsDir)) {
  fs.mkdirSync(rawAssetsDir, { recursive: true })
}

// 资产文件路径
const assetFilePath = path.join(rawAssetsDir, 'assets.csv')

// 初始化资产文件（如果不存在）
if (!fs.existsSync(assetFilePath)) {
  const initialContent = '账户分类,币种,金额,描述,时间,对应人民币金额,资产/负债\n'
  fs.writeFileSync(assetFilePath, initialContent)
}

// API路由

/**
 * GET /api/assets - 获取所有资产
 */
app.get('/api/assets', (req, res) => {
  try {
    const csvData = fs.readFileSync(assetFilePath, 'utf-8')
    // 简单解析CSV数据
    const lines = csvData.trim().split('\n')
    if (lines.length < 2) {
      res.json([])
      return
    }

    // 解析表头
    const headers = lines[0].split(',').map(header => header.trim())
    
    // 解析数据行
    const assets: any[] = []
    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(value => value.trim())
      if (values.length !== headers.length) continue

      // 创建资产对象
      const asset: any = {
        id: `${i}` // 简单ID
      }

      // 映射表头到资产对象属性
      for (let j = 0; j < headers.length; j++) {
        const header = headers[j]
        const value = values[j]

        switch (header) {
          case '账户分类':
            asset.accountType = value
            break
          case '币种':
            asset.currency = value
            break
          case '金额':
            asset.amount = parseFloat(value) || 0
            break
          case '描述':
            asset.description = value
            break
          case '时间':
            asset.timestamp = value
            break
          case '对应人民币金额':
            asset.cnyAmount = parseFloat(value) || 0
            break
          case '资产/负债':
            asset.assetOrLiability = value
            break
          default:
            // 忽略未知字段
            break
        }
      }

      assets.push(asset)
    }

    res.json(assets)
  } catch (error) {
    console.error('读取资产数据失败:', error)
    res.status(500).json({ error: '读取资产数据失败' })
  }
})

/**
 * POST /api/assets - 添加新资产
 */
app.post('/api/assets', (req, res) => {
  try {
    const { accountType, currency, amount, description } = req.body
    
    // 读取现有数据
    const csvData = fs.readFileSync(assetFilePath, 'utf-8')
    const lines = csvData.trim().split('\n')
    
    // 生成新资产数据行
    const timestamp = new Date().toISOString()
    const cnyAmount = currency === 'CNY' ? amount : (amount * 7.2).toFixed(2) // 简单汇率计算
    const assetOrLiability = accountType === '信用卡' ? '负债' : '资产'
    
    const newLine = `${accountType},${currency},${amount},${description},${timestamp},${cnyAmount},${assetOrLiability}`
    
    // 添加到CSV文件
    const updatedCsvData = csvData.trim() + '\n' + newLine
    fs.writeFileSync(assetFilePath, updatedCsvData)
    
    // 返回创建的资产
    const newAsset = {
      id: `${lines.length}`,
      accountType,
      currency,
      amount: parseFloat(amount),
      description,
      timestamp,
      cnyAmount: parseFloat(cnyAmount),
      assetOrLiability
    }
    
    res.status(201).json(newAsset)
  } catch (error) {
    console.error('添加资产失败:', error)
    res.status(500).json({ error: '添加资产失败' })
  }
})

/**
 * PUT /api/assets/:id - 更新资产
 */
app.put('/api/assets/:id', (req, res) => {
  try {
    const { id } = req.params
    const { accountType, currency, amount, description } = req.body
    
    // 读取现有数据
    const csvData = fs.readFileSync(assetFilePath, 'utf-8')
    const lines = csvData.trim().split('\n')
    
    if (parseInt(id) >= lines.length) {
      return res.status(404).json({ error: '未找到指定资产' })
    }
    
    // 更新资产数据行
    const timestamp = new Date().toISOString()
    const cnyAmount = currency === 'CNY' ? amount : (amount * 7.2).toFixed(2) // 简单汇率计算
    const assetOrLiability = accountType === '信用卡' ? '负债' : '资产'
    
    const updatedLine = `${accountType},${currency},${amount},${description},${timestamp},${cnyAmount},${assetOrLiability}`
    lines[parseInt(id)] = updatedLine
    
    // 保存到文件
    const updatedCsvData = lines.join('\n')
    fs.writeFileSync(assetFilePath, updatedCsvData)
    
    // 返回更新的资产
    const updatedAsset = {
      id,
      accountType,
      currency,
      amount: parseFloat(amount),
      description,
      timestamp,
      cnyAmount: parseFloat(cnyAmount),
      assetOrLiability
    }
    
    res.json(updatedAsset)
  } catch (error) {
    console.error('更新资产失败:', error)
    res.status(500).json({ error: '更新资产失败' })
  }
})

/**
 * DELETE /api/assets/:id - 删除资产
 */
app.delete('/api/assets/:id', (req, res) => {
  try {
    const { id } = req.params
    
    // 读取现有数据
    const csvData = fs.readFileSync(assetFilePath, 'utf-8')
    const lines = csvData.trim().split('\n')
    
    if (parseInt(id) >= lines.length || parseInt(id) < 1) {
      return res.status(404).json({ error: '未找到指定资产' })
    }
    
    // 过滤掉要删除的资产
    const updatedLines = lines.filter((_, index) => index !== parseInt(id))
    
    // 保存到文件
    const updatedCsvData = updatedLines.join('\n')
    fs.writeFileSync(assetFilePath, updatedCsvData)
    
    res.json({ message: '资产删除成功' })
  } catch (error) {
    console.error('删除资产失败:', error)
    res.status(500).json({ error: '删除资产失败' })
  }
})

// 启动服务器
app.listen(PORT, () => {
  console.log(`资产管理API服务器运行在端口 ${PORT}`)
})