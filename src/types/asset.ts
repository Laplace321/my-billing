// 资产数据接口定义
export interface Asset {
  id: string // 唯一标识符
  accountType: string // 账户分类 (支付账户、信用卡、其他资产)
  currency: string // 币种 (CNY, USD, EUR等)
  amount: number // 金额
  description: string // 描述
  timestamp?: string // 时间戳 (可选，由系统生成)
  cnyAmount?: number // 对应人民币金额 (可选，由系统计算)
  assetOrLiability?: '资产' | '负债' // 资产/负债 (可选，由系统判断)
}

// 账户分类枚举
export enum AccountType {
  PAYMENT = '支付账户',
  CREDIT_CARD = '信用卡',
  OTHER_ASSET = '其他资产'
}

// 货币枚举
export enum Currency {
  CNY = 'CNY',
  USD = 'USD',
  EUR = 'EUR',
  JPY = 'JPY',
  HKD = 'HKD'
}