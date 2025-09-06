#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
账单去重工具
用于处理重复的账单记录
"""

import pandas as pd


class BillDeduplicator:
    """
    账单去重器类
    """
    
    def __init__(self):
        """
        初始化去重器
        """
        pass
    
    def _filter_transfer_pairs(self, df):
        """
        过滤同一交易对象的一对支出和收入转账
        支持支付宝、微信、银行之间的相互转账过滤
        
        Args:
            df: 原始数据
            
        Returns:
            过滤后的数据
        """
        if '代理' not in df.columns or '金额' not in df.columns:
            return df
            
        # 获取所有唯一的交易对方
        unique_agents = df['代理'].unique()
        processed_agents = set()
        rows_to_drop = []
        
        for agent in unique_agents:
            if agent in processed_agents or not isinstance(agent, str):
                continue
                
            # 查找与当前agent相似的所有agent（处理a.k.a. 小黄蜂(**咏)和**咏这样的情况）
            similar_agents = self._find_similar_agents(agent, unique_agents)
            
            # 标记已处理的agent
            for similar_agent in similar_agents:
                processed_agents.add(similar_agent)
            
            # 获取所有相似agent的记录
            agent_mask = df['代理'].isin(similar_agents)
            agent_records = df[agent_mask]
            
            if len(agent_records) > 1:
                # 特殊处理：如果包含支付宝的转账记录，则保留这些记录
                alipay_records = agent_records[agent_records['源账户'] == '支付宝']
                if not alipay_records.empty:
                    # 保留支付宝记录，只过滤其他记录中的重复项
                    # 检查非支付宝记录中是否有与支付宝记录匹配的转账对
                    for _, alipay_row in alipay_records.iterrows():
                        alipay_amount = alipay_row['金额']
                        alipay_date = str(alipay_row['日期']).split(' ')[0]  # 只取日期部分
                        
                        # 检查其他记录中是否有匹配的转账
                        other_records = agent_records[agent_records['源账户'] != '支付宝']
                        for idx, other_row in other_records.iterrows():
                            other_amount = other_row['金额']
                            other_date = str(other_row['日期']).split(' ')[0]  # 只取日期部分
                            
                            # 如果金额相同但符号相反，且日期相同，则标记为需要删除的重复记录
                            if (abs(alipay_amount + other_amount) < 0.01 and 
                                alipay_amount * other_amount < 0 and 
                                alipay_date == other_date):
                                print(f"发现转账对: 交易对方={agent}, 金额={abs(alipay_amount)}")
                                rows_to_drop.append(idx)  # 只删除非支付宝记录
                else:
                    # 没有支付宝记录，按正常逻辑处理
                    # 检查是否有金额相同但符号相反的记录（转账对）
                    matched_pairs = set()  # 记录已匹配的索引对，避免重复处理
                    for i, (idx1, row1) in enumerate(agent_records.iterrows()):
                        amount1 = row1['金额']
                        for j, (idx2, row2) in enumerate(agent_records.iterrows()):
                            # 不比较同一条记录，且未被匹配过
                            if idx1 != idx2 and idx1 not in matched_pairs and idx2 not in matched_pairs:
                                amount2 = row2['金额']
                                # 如果金额相同但符号相反，则标记为需要删除的转账对
                                if abs(amount1 + amount2) < 0.01 and amount1 * amount2 < 0:
                                    print(f"发现转账对: 交易对方={agent}, 金额={abs(amount1)}")
                                    rows_to_drop.extend([idx1, idx2])
                                    matched_pairs.add(idx1)
                                    matched_pairs.add(idx2)
                                    break
        
        # 删除标记的行
        if rows_to_drop:
            df = df.drop(rows_to_drop)
            
        return df
    
    def _find_similar_agents(self, agent, all_agents):
        """
        查找与给定agent相似的agents
        处理a.k.a. 小黄蜂这样的情况
        
        Args:
            agent: 目标agent
            all_agents: 所有agents列表
            
        Returns:
            相似的agents列表
        """
        if not agent or not isinstance(agent, str):
            return [agent] if agent in all_agents else []
            
        similar_agents = [agent]  # 包含自己
        
        # 处理a.k.a. 小黄蜂这样的情况
        if 'a.k.a.' in agent and '(**' in agent:
            # 提取基础名称（如"小黄蜂"）
            base_name = agent.split('a.k.a. ')[1].split('(**')[0]
            similar_agents.append(base_name)
            
            # 提取括号内的名称（如"**咏"）
            if ')' in agent:
                suffix = agent.split('(**')[1].split(')')[0]
                similar_agents.append(suffix)
        
        # 处理其他情况
        for other_agent in all_agents:
            if not other_agent or not isinstance(other_agent, str):
                continue
                
            # 如果other_agent是agent的一部分，或者agent是other_agent的一部分
            if agent in other_agent or other_agent in agent:
                similar_agents.append(other_agent)
        
        # 去重并返回
        return list(set(similar_agents))
    
    def deduplicate_bills(self, bills_data):
        """
        对账单进行去重处理
        
        根据规则，因存在支付宝账单用银行卡支付的情况，
        导致同一笔订单记录两次，可根据付款时间、金额是否相同进行去重判断，
        优先保留支付宝或微信的账单。
        
        Args:
            bills_data: 账单数据列表，每个元素为pandas DataFrame
            
        Returns:
            去重后的账单数据
        """
        if not bills_data:
            return None
            
        # 合并所有账单数据
        if len(bills_data) == 1:
            merged_data = bills_data[0]
        else:
            merged_data = pd.concat(bills_data, ignore_index=True)
        
        if merged_data.empty:
            return merged_data
            
        print(f"合并后总记录数: {len(merged_data)}")
        
        # 先过滤同一交易对象的一对支出和收入转账
        original_count = len(merged_data)
        merged_data = self._filter_transfer_pairs(merged_data)
        after_transfer_filter = len(merged_data)
        if original_count != after_transfer_filter:
            print(f"转账对过滤后剩余 {after_transfer_filter} 条记录，过滤了 {original_count - after_transfer_filter} 条记录")
        
        # 根据付款时间、金额去重，优先保留支付宝或微信的账单
        # 先按日期和金额分组
        if '日期' in merged_data.columns and '金额' in merged_data.columns:
            # 创建一个用于去重的辅助列
            # 标准化日期格式，只保留日期部分用于比较
            def normalize_date_for_comparison(date_str):
                if not isinstance(date_str, str):
                    return ""
                # 只保留日期部分（YYYY-MM-DD）
                return date_str.split(' ')[0]
            
            # 为去重创建标准化的日期金额标识
            merged_data['_comparison_date'] = merged_data['日期'].apply(normalize_date_for_comparison)
            merged_data['_comparison_key'] = merged_data['_comparison_date'].astype(str) + '_' + merged_data['金额'].astype(str)
            
            # 按标准化的日期和金额分组
            grouped = merged_data.groupby('_comparison_key')
            
            # 对每组数据进行处理，优先保留支付宝或微信的账单
            deduplicated_rows = []
            duplicate_count = 0
            for name, group in grouped:
                if len(group) == 1:
                    # 没有重复，直接添加
                    deduplicated_rows.append(group.iloc[0])
                else:
                    # 有重复，但需要特殊处理转账记录
                    duplicate_count += len(group) - 1
                    
                    # 检查是否为转账记录（正负金额配对）
                    amounts = group['金额'].tolist()
                    is_transfer_pair = False
                    if len(amounts) == 2:
                        try:
                            amount1 = float(str(amounts[0]).replace(',', ''))
                            amount2 = float(str(amounts[1]).replace(',', ''))
                            # 如果金额相同但符号相反，则为转账对
                            if abs(amount1 + amount2) < 0.01 and amount1 * amount2 < 0:
                                is_transfer_pair = True
                        except:
                            pass
                    
                    if is_transfer_pair:
                        # 是转账对，优先保留支付宝或微信的记录
                        alipay_records = group[group['源账户'] == '支付宝'] if '源账户' in group.columns else pd.DataFrame()
                        wechat_records = group[group['源账户'] == '微信'] if '源账户' in group.columns else pd.DataFrame()
                        bank_records = group[group['源账户'] == '银行'] if '源账户' in group.columns else pd.DataFrame()
                        
                        # 特殊处理：对于转账类记录，优先保留支付宝或微信的记录
                        if not alipay_records.empty:
                            # 优先选择支付宝记录
                            deduplicated_rows.append(alipay_records.iloc[0])
                        elif not wechat_records.empty:
                            # 其次选择微信记录
                            deduplicated_rows.append(wechat_records.iloc[0])
                        elif not bank_records.empty:
                            # 最后选择银行记录
                            deduplicated_rows.append(bank_records.iloc[0])
                        else:
                            # 都没有，选择第一条记录
                            deduplicated_rows.append(group.iloc[0])
                    else:
                        # 不是转账对，可能是重复记录，按优先级保留
                        alipay_records = group[group['源账户'] == '支付宝'] if '源账户' in group.columns else pd.DataFrame()
                        wechat_records = group[group['源账户'] == '微信'] if '源账户' in group.columns else pd.DataFrame()
                        bank_records = group[group['源账户'] == '银行'] if '源账户' in group.columns else pd.DataFrame()
                        
                        # 按优先级保留记录
                        if not alipay_records.empty:
                            # 优先选择支付宝记录
                            deduplicated_rows.append(alipay_records.iloc[0])
                        elif not wechat_records.empty:
                            # 其次选择微信记录
                            deduplicated_rows.append(wechat_records.iloc[0])
                        elif not bank_records.empty:
                            # 最后选择银行记录
                            deduplicated_rows.append(bank_records.iloc[0])
                        else:
                            # 都没有，选择第一条记录
                            deduplicated_rows.append(group.iloc[0])
            
            # 构建最终结果
            result = pd.DataFrame(deduplicated_rows)
            # 删除辅助列
            auxiliary_columns = ['_comparison_date', '_comparison_key']
            for col in auxiliary_columns:
                if col in result.columns:
                    result = result.drop(col, axis=1)
            
            print(f"去重后剩余 {len(result)} 条记录，去重了 {duplicate_count} 条记录")
            return result
        
        return merged_data
    
    def _get_unique_parties(self, parties):
        """
        从交易对方列表中提取唯一的基础交易对象
        
        Args:
            parties: 交易对方列表
            
        Returns:
            唯一的基础交易对象列表
        """
        unique_parties = []
        for party in parties:
            is_similar = False
            for unique_party in unique_parties:
                if self._is_same_party(party, unique_party):
                    is_similar = True
                    break
            if not is_similar:
                unique_parties.append(party)
        return unique_parties
    
    def _is_same_party(self, party1, party2):
        """
        判断两个交易对方是否为同一对象
        
        Args:
            party1: 交易对方1
            party2: 交易对方2
            
        Returns:
            是否为同一对象
        """
        # 处理a.k.a.开头的特殊情况
        if party1.startswith('a.k.a. ') and party2.startswith('a.k.a. '):
            # 提取基础名称（去除括号内容）
            base1 = party1.split('(')[0] if '(' in party1 else party1
            base2 = party2.split('(')[0] if '(' in party2 else party2
            return base1 == base2
        
        # 其他情况直接比较
        return party1 == party2