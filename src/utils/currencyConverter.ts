// 货币转换工具
import { Currency } from '../types/asset'

/**
 * 获取货币汇率（相对于人民币）
 * @param currency 货币代码
 * @returns 对应货币到人民币的汇率
 */
export function getExchangeRate(currency: string): number {
  // 预设汇率（作为备选方案）
  const exchangeRates: Record<string, number> = {
    'CNY': 1.0,
    'USD': 7.2,
    'EUR': 7.8,
    'JPY': 0.05,
    'HKD': 0.92,
  }

  return exchangeRates[currency.toUpperCase()] || 1.0
}

/**
 * 将指定货币金额转换为人民币金额
 * @param amount 金额
 * @param currency 货币代码
 * @returns 对应人民币金额
 */
export function convertToCNY(amount: number, currency: string): number {
  const rate = getExchangeRate(currency)
  return Math.round(amount * rate * 100) / 100 // 保留两位小数
}

/**
 * 根据账户分类判断资产或负债
 * @param accountType 账户分类
 * @returns '资产' 或 '负债'
 */
export function determineAssetOrLiability(accountType: string): '资产' | '负债' {
  return accountType === '信用卡' ? '负债' : '资产'
}