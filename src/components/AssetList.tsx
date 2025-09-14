// 资产列表组件
import React, { useState } from 'react'
import { Asset } from '../types/asset'
import assetService from '../services/assetService'
import AssetForm from './AssetForm'

interface AssetListProps {
  assets: Asset[]
  onAssetsChange: (assets: Asset[]) => void
}

/**
 * 资产列表组件
 * 显示资产列表并提供添加、编辑和删除功能
 */
const AssetList: React.FC<AssetListProps> = ({ assets, onAssetsChange }) => {
  const [editingAsset, setEditingAsset] = useState<Asset | null>(null)
  const [isFormVisible, setIsFormVisible] = useState(false)

  /**
   * 处理编辑资产
   * @param asset 要编辑的资产
   */
  const handleEdit = (asset: Asset) => {
    setEditingAsset(asset)
    setIsFormVisible(true)
  }

  /**
   * 处理删除资产
   * @param id 资产ID
   */
  const handleDelete = async (id: string) => {
    if (window.confirm('确定要删除这个资产吗？')) {
      const success = await assetService.deleteAsset(id)
      if (success) {
        // 重新加载资产数据
        const updatedAssets = await assetService.loadAssets()
        onAssetsChange(updatedAssets)
      }
    }
  }

  /**
   * 处理表单提交
   * @param asset 资产数据（不包含自动生成的字段）
   */
  const handleFormSubmit = async (asset: Omit<Asset, 'id' | 'timestamp' | 'cnyAmount' | 'assetOrLiability'>) => {
    try {
      if (editingAsset) {
        // 更新现有资产
        await assetService.updateAsset(editingAsset.id, asset)
      } else {
        // 添加新资产
        await assetService.addAsset(asset)
      }

      // 重新加载资产数据
      const updatedAssets = await assetService.loadAssets()
      onAssetsChange(updatedAssets)
      
      // 重置表单状态
      setEditingAsset(null)
      setIsFormVisible(false)
    } catch (error) {
      console.error('操作资产失败:', error)
      alert('操作资产失败，请重试')
    }
  }

  /**
   * 处理取消编辑
   */
  const handleCancel = () => {
    setEditingAsset(null)
    setIsFormVisible(false)
  }

  return (
    <div className="asset-list">
      <div className="list-header">
        <h2>资产列表</h2>
        <button 
          className="add-button"
          onClick={() => {
            setEditingAsset(null)
            setIsFormVisible(true)
          }}
        >
          添加资产
        </button>
      </div>

      {isFormVisible && (
        <div className="form-overlay">
          <div className="form-container">
            <AssetForm 
              asset={editingAsset} 
              onSubmit={handleFormSubmit}
              onCancel={handleCancel}
            />
          </div>
        </div>
      )}

      <div className="table-container">
        <table className="asset-table">
          <thead>
            <tr>
              <th>账户分类</th>
              <th>币种</th>
              <th>金额</th>
              <th>对应人民币金额</th>
              <th>资产/负债</th>
              <th>描述</th>
              <th>时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {assets.map(asset => (
              <tr key={asset.id}>
                <td>{asset.accountType}</td>
                <td>{asset.currency}</td>
                <td>{asset.amount.toFixed(2)}</td>
                <td>{asset.cnyAmount?.toFixed(2) || '0.00'}</td>
                <td>
                  <span className={`status ${asset.assetOrLiability === '资产' ? 'asset' : 'liability'}`}>
                    {asset.assetOrLiability}
                  </span>
                </td>
                <td>{asset.description}</td>
                <td>{asset.timestamp ? new Date(asset.timestamp).toLocaleString() : ''}</td>
                <td>
                  <button 
                    className="edit-button"
                    onClick={() => handleEdit(asset)}
                  >
                    编辑
                  </button>
                  <button 
                    className="delete-button"
                    onClick={() => handleDelete(asset.id)}
                  >
                    删除
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default AssetList