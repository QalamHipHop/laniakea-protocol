"""
Laniakea Protocol - SCDA Neural Network Module
ماژول شبکه عصبی SCDA برای مدل‌سازی دانش به صورت یک گراف متصل
Version: 0.0.01
Copyright: LaniakeA Protocol
"""

import uuid
import numpy as np
from typing import Dict, List, Set, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import json


@dataclass
class KnowledgeNode:
    """یک گره در شبکه عصبی SCDA که یک مفهوم دانش را نشان می‌دهد"""
    
    node_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    concept_name: str = ""
    domain: str = ""  # حوزه دانش (e.g., "mathematics", "physics")
    activation_level: float = 0.0  # سطح فعال‌سازی گره [0, 1]
    strength: float = 0.5  # قدرت گره (تأثیر در شبکه)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # متادیتا
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_activation(self, new_level: float):
        """به‌روزرسانی سطح فعال‌سازی گره"""
        self.activation_level = np.clip(new_level, 0.0, 1.0)
        self.last_updated = datetime.now().isoformat()
    
    def strengthen(self, amount: float = 0.1):
        """تقویت قدرت گره"""
        self.strength = np.clip(self.strength + amount, 0.0, 1.0)
        self.last_updated = datetime.now().isoformat()
    
    def weaken(self, amount: float = 0.05):
        """ضعیف کردن قدرت گره"""
        self.strength = np.clip(self.strength - amount, 0.0, 1.0)
        self.last_updated = datetime.now().isoformat()


@dataclass
class KnowledgeEdge:
    """یک لبه در شبکه عصبی SCDA که ارتباط بین دو مفهوم را نشان می‌دهد"""
    
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    source_node_id: str = ""
    target_node_id: str = ""
    weight: float = 0.5  # وزن ارتباط [0, 1]
    edge_type: str = "association"  # نوع ارتباط (association, causation, similarity, etc.)
    strength: float = 0.5  # قدرت ارتباط
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def update_weight(self, new_weight: float):
        """به‌روزرسانی وزن لبه"""
        self.weight = np.clip(new_weight, 0.0, 1.0)
    
    def strengthen(self, amount: float = 0.1):
        """تقویت ارتباط"""
        self.strength = np.clip(self.strength + amount, 0.0, 1.0)
    
    def weaken(self, amount: float = 0.05):
        """ضعیف کردن ارتباط"""
        self.strength = np.clip(self.strength - amount, 0.0, 1.0)


class SCDANeuralNetwork:
    """شبکه عصبی SCDA برای نمایش و پردازش دانش"""
    
    def __init__(self, scda_id: str):
        self.scda_id = scda_id
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.edges: Dict[str, KnowledgeEdge] = {}
        self.activation_history: List[Dict[str, Any]] = []
        self.created_at = datetime.now().isoformat()
    
    def add_node(self, concept_name: str, domain: str, initial_strength: float = 0.5) -> KnowledgeNode:
        """افزودن یک گره جدید به شبکه"""
        node = KnowledgeNode(
            concept_name=concept_name,
            domain=domain,
            strength=initial_strength
        )
        self.nodes[node.node_id] = node
        return node
    
    def add_edge(self, source_node_id: str, target_node_id: str, 
                edge_type: str = "association", weight: float = 0.5) -> Optional[KnowledgeEdge]:
        """افزودن یک لبه جدید بین دو گره"""
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            return None
        
        edge = KnowledgeEdge(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_type=edge_type,
            weight=weight
        )
        self.edges[edge.edge_id] = edge
        return edge
    
    def activate_node(self, node_id: str, activation_level: float):
        """فعال‌سازی یک گره"""
        if node_id not in self.nodes:
            return False
        
        node = self.nodes[node_id]
        node.update_activation(activation_level)
        
        # انتشار فعال‌سازی به گره‌های متصل
        self._propagate_activation(node_id, activation_level)
        
        return True
    
    def _propagate_activation(self, source_node_id: str, activation_level: float, depth: int = 1, max_depth: int = 3):
        """انتشار فعال‌سازی از یک گره به گره‌های متصل"""
        if depth > max_depth:
            return
        
        # پیدا کردن لبه‌های خروجی از این گره
        outgoing_edges = [e for e in self.edges.values() if e.source_node_id == source_node_id]
        
        for edge in outgoing_edges:
            target_node = self.nodes[edge.target_node_id]
            
            # محاسبه فعال‌سازی جدید بر اساس وزن لبه
            propagated_activation = activation_level * edge.weight * edge.strength
            
            # به‌روزرسانی فعال‌سازی گره هدف
            new_activation = (target_node.activation_level + propagated_activation) / 2
            target_node.update_activation(new_activation)
            
            # انتشار بیشتر
            self._propagate_activation(edge.target_node_id, new_activation, depth + 1, max_depth)
    
    def learn_from_problem(self, problem_data: Dict[str, Any], solution_quality: float):
        """یادگیری از حل یک مسئله و به‌روزرسانی شبکه"""
        
        # استخراج مفاهیم مرتبط با مسئله
        required_domains = problem_data.get("K_req", [])
        
        # تقویت گره‌های مرتبط
        for domain in required_domains:
            # پیدا کردن گره‌های این حوزه
            domain_nodes = [n for n in self.nodes.values() if n.domain == domain]
            
            for node in domain_nodes:
                # تقویت گره بر اساس کیفیت راه‌حل
                strengthening_amount = solution_quality * 0.2
                node.strengthen(strengthening_amount)
                
                # فعال‌سازی گره
                node.update_activation(solution_quality)
        
        # ایجاد ارتباطات جدید بین مفاهیم
        if len(domain_nodes) > 1:
            for i in range(len(domain_nodes) - 1):
                for j in range(i + 1, len(domain_nodes)):
                    # بررسی اینکه آیا لبه‌ای بین این دو گره وجود دارد
                    existing_edge = None
                    for edge in self.edges.values():
                        if ((edge.source_node_id == domain_nodes[i].node_id and 
                             edge.target_node_id == domain_nodes[j].node_id) or
                            (edge.source_node_id == domain_nodes[j].node_id and 
                             edge.target_node_id == domain_nodes[i].node_id)):
                            existing_edge = edge
                            break
                    
                    if existing_edge:
                        # تقویت لبه موجود
                        existing_edge.strengthen(solution_quality * 0.1)
                    else:
                        # ایجاد لبه جدید
                        self.add_edge(
                            domain_nodes[i].node_id,
                            domain_nodes[j].node_id,
                            edge_type="learned_association",
                            weight=solution_quality
                        )
    
    def calculate_network_complexity(self) -> float:
        """محاسبه پیچیدگی شبکه بر اساس تعداد گره‌ها و لبه‌ها"""
        node_complexity = len(self.nodes) * 0.1
        edge_complexity = len(self.edges) * 0.05
        
        # وزن‌دهی بر اساس قدرت گره‌ها و لبه‌ها
        node_strength_sum = sum(n.strength for n in self.nodes.values())
        edge_strength_sum = sum(e.strength for e in self.edges.values())
        
        avg_node_strength = node_strength_sum / len(self.nodes) if self.nodes else 0
        avg_edge_strength = edge_strength_sum / len(self.edges) if self.edges else 0
        
        total_complexity = (node_complexity + edge_complexity) * (avg_node_strength + avg_edge_strength) / 2
        
        return np.clip(total_complexity, 0.0, 1.0)
    
    def get_most_active_nodes(self, limit: int = 10) -> List[KnowledgeNode]:
        """دریافت فعال‌ترین گره‌های شبکه"""
        sorted_nodes = sorted(
            self.nodes.values(),
            key=lambda n: n.activation_level * n.strength,
            reverse=True
        )
        return sorted_nodes[:limit]
    
    def get_network_summary(self) -> Dict[str, Any]:
        """دریافت خلاصه‌ای از شبکه"""
        return {
            "scda_id": self.scda_id,
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "network_complexity": self.calculate_network_complexity(),
            "avg_node_activation": np.mean([n.activation_level for n in self.nodes.values()]) if self.nodes else 0,
            "avg_node_strength": np.mean([n.strength for n in self.nodes.values()]) if self.nodes else 0,
            "avg_edge_weight": np.mean([e.weight for e in self.edges.values()]) if self.edges else 0,
            "created_at": self.created_at
        }
    
    def export_to_json(self) -> str:
        """صادر کردن شبکه به فرمت JSON"""
        export_data = {
            "scda_id": self.scda_id,
            "nodes": [
                {
                    "node_id": n.node_id,
                    "concept_name": n.concept_name,
                    "domain": n.domain,
                    "activation_level": n.activation_level,
                    "strength": n.strength
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "edge_id": e.edge_id,
                    "source_node_id": e.source_node_id,
                    "target_node_id": e.target_node_id,
                    "weight": e.weight,
                    "edge_type": e.edge_type,
                    "strength": e.strength
                }
                for e in self.edges.values()
            ],
            "summary": self.get_network_summary()
        }
        return json.dumps(export_data, indent=2, ensure_ascii=False)
