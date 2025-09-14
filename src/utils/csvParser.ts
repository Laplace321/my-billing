// CSV解析工具
import { Asset } from '../types/asset'

/**
 * 解析CSV字符串为资产对象数组
 * @param csvString CSV格式的字符串
 * @returns 资产对象数组
 */
export function parseCSV(csvString: string): Asset[] {
  const lines = csvString.trim().split('\n')
  if (lines.length < 2) return []

  // 解析表头
  const headers = lines[0].split(',').map(header => header.trim())
  
  // 解析数据行
  const assets: Asset[] = []
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(',').map(value => value.trim())
    if (values.length !== headers.length) continue

    // 创建资产对象
    const asset: any = {
      id: generateId() // 生成唯一ID
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
          asset.assetOrLiability = value as '资产' | '负债'
          break
        default:
          // 忽略未知字段
          break
      }
    }

    assets.push(asset)
  }

  return assets
}

/**
 * 将资产对象数组转换为CSV字符串
 * @param assets 资产对象数组
 * @returns CSV格式的字符串
 */
export function convertToCSV(assets: Asset[]): string {
  if (assets.length === 0) return ''

  // 定义表头
  const headers = ['账户分类', '币种', '金额', '描述', '时间', '对应人民币金额', '资产/负债']
  
  // 创建CSV内容
  let csvContent = headers.join(',') + '\n'

  // 添加数据行
  for (const asset of assets) {
    const values = [
      asset.accountType,
      asset.currency,
      asset.amount.toString(),
      asset.description,
      asset.timestamp || new Date().toISOString(),
      (asset.cnyAmount || 0).toString(),
      asset.assetOrLiability || (asset.accountType === '信用卡' ? '负债' : '资产')
    ]
    
    csvContent += values.join(',') + '\n'
  }

  return csvContent
}

/**
 * 生成唯一ID
 * @returns 唯一ID字符串
 */
function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).substring(2)
}