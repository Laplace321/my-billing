// 资产数据服务
import { Asset } from '../types/asset'
import { convertToCNY, determineAssetOrLiability } from '../utils/currencyConverter'

// API基础URL - 使用相对路径以便与后端API一起部署
const API_BASE_URL = '/api/assets'

/**
 * 资产服务类
 * 处理资产数据的读取、保存和管理
 */
class AssetService {
  /**
   * 从API获取资产数据
   * @returns 资产对象数组
   */
  async loadAssets(): Promise<Asset[]> {
    try {
      const response = await fetch(API_BASE_URL)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const assets = await response.json()
      return assets
    } catch (error) {
      console.error('读取资产数据失败:', error)
      throw new Error('读取资产数据失败')
    }
  }

  /**
   * 添加新资产
   * @param asset 新资产对象（不包含id、timestamp、cnyAmount和assetOrLiability字段）
   * @returns 添加的完整资产对象
   */
  async addAsset(asset: Omit<Asset, 'id' | 'timestamp' | 'cnyAmount' | 'assetOrLiability'>): Promise<Asset> {
    try {
      const response = await fetch(API_BASE_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(asset),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const newAsset = await response.json()
      return newAsset
    } catch (error) {
      console.error('添加资产失败:', error)
      throw new Error('添加资产失败')
    }
  }

  /**
   * 更新资产
   * @param id 要更新的资产ID
   * @param asset 更新的资产对象（不包含id、timestamp、cnyAmount和assetOrLiability字段）
   * @returns 更新后的完整资产对象
   */
  async updateAsset(id: string, asset: Omit<Asset, 'id' | 'timestamp' | 'cnyAmount' | 'assetOrLiability'>): Promise<Asset> {
    try {
      const response = await fetch(`${API_BASE_URL}/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(asset),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const updatedAsset = await response.json()
      return updatedAsset
    } catch (error) {
      console.error('更新资产失败:', error)
      throw new Error('更新资产失败')
    }
  }

  /**
   * 删除资产
   * @param id 要删除的资产ID
   * @returns 是否删除成功
   */
  async deleteAsset(id: string): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/${id}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return true
    } catch (error) {
      console.error('删除资产失败:', error)
      return false
    }
  }
}

// 导出单例实例
const assetService = new AssetService()
export default assetService