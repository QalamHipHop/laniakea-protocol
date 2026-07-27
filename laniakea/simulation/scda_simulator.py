"""
Laniakea Protocol - SCDA Evolutionary Simulator
شبیه‌ساز تکاملی SCDA برای سناریوهای "چه می‌شد اگر" (What-If)
Version: 2.0.0
"""

import copy
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from laniakea.intelligence.scda_model import SingleCellDigitalAccount, breed_scdas, predict_child_traits
from laniakea.intelligence.brain import CosmicBrainAI


class SCDASimulationScenario:
    """
    یک سناریوی شبیه‌سازی برای تست تأثیر تصمیمات مختلف بر روی SCDA
    """
    
    def __init__(self, scenario_name: str, description: str):
        self.scenario_name = scenario_name
        self.description = description
        self.scda_snapshots: List[Dict[str, Any]] = []
        self.events: List[Dict[str, Any]] = []
        self.created_at = datetime.now().isoformat()
    
    def add_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        افزودن یک رویداد به سناریو
        
        :param event_type: نوع رویداد (e.g., "problem_solved", "breeding", "mutation")
        :param event_data: داده‌های رویداد
        """
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": event_data
        }
        self.events.append(event)
    
    def add_scda_snapshot(self, scda: SingleCellDigitalAccount, step: int):
        """
        ذخیره یک عکس‌العمل از وضعیت SCDA در یک نقطه زمانی
        
        :param scda: SCDA
        :param step: شماره گام شبیه‌سازی
        """
        snapshot = {
            "step": step,
            "timestamp": datetime.now().isoformat(),
            "state": scda.get_state(),
            "dna_diversity": scda.dna.calculate_genetic_diversity()
        }
        self.scda_snapshots.append(snapshot)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        دریافت خلاصه سناریو
        
        :return: خلاصه شامل تغییرات کلیدی
        """
        if not self.scda_snapshots:
            return {"error": "No snapshots recorded"}
        
        initial_state = self.scda_snapshots[0]["state"]
        final_state = self.scda_snapshots[-1]["state"]
        
        complexity_change = final_state["complexity_index"] - initial_state["complexity_index"]
        energy_change = final_state["energy"] - initial_state["energy"]
        knowledge_change = final_state["knowledge_count"] - initial_state["knowledge_count"]
        
        return {
            "scenario_name": self.scenario_name,
            "description": self.description,
            "total_steps": len(self.scda_snapshots),
            "total_events": len(self.events),
            "complexity_change": complexity_change,
            "energy_change": energy_change,
            "knowledge_change": knowledge_change,
            "initial_complexity": initial_state["complexity_index"],
            "final_complexity": final_state["complexity_index"],
            "initial_energy": initial_state["energy"],
            "final_energy": final_state["energy"]
        }


class SCDAEvolutionarySimulator:
    """
    شبیه‌ساز تکاملی SCDA برای سناریوهای What-If
    """
    
    def __init__(self, scda: SingleCellDigitalAccount, brain: Optional[CosmicBrainAI] = None):
        self.original_scda = scda
        self.simulated_scda = copy.deepcopy(scda)
        self.brain = brain or CosmicBrainAI(f"simulator_{scda.identity[:8]}")
        self.current_scenario: Optional[SCDASimulationScenario] = None
        self.scenarios: List[SCDASimulationScenario] = []
    
    def create_scenario(self, scenario_name: str, description: str) -> SCDASimulationScenario:
        """
        ایجاد یک سناریوی جدید
        
        :param scenario_name: نام سناریو
        :param description: توضیح سناریو
        :return: شیء سناریو
        """
        # بازنشانی SCDA شبیه‌سازی شده
        self.simulated_scda = copy.deepcopy(self.original_scda)
        
        # ایجاد سناریو جدید
        self.current_scenario = SCDASimulationScenario(scenario_name, description)
        self.scenarios.append(self.current_scenario)
        
        # ذخیره وضعیت اولیه
        self.current_scenario.add_scda_snapshot(self.simulated_scda, 0)
        
        return self.current_scenario
    
    def simulate_problem_solving(self, problem_difficulty: float, solution_quality: float, 
                                num_attempts: int = 1) -> Dict[str, Any]:
        """
        شبیه‌سازی حل مسائل
        
        :param problem_difficulty: دشواری مسئله
        :param solution_quality: کیفیت راه‌حل
        :param num_attempts: تعداد تلاش‌ها
        :return: نتایج شبیه‌سازی
        """
        if not self.current_scenario:
            raise ValueError("No active scenario. Create a scenario first.")
        
        results = {
            "total_attempts": num_attempts,
            "successful_attempts": 0,
            "complexity_gains": [],
            "energy_changes": []
        }
        
        for i in range(num_attempts):
            # اعتبارسنجی دوگانه
            is_valid = self.brain.dual_validation(
                self.simulated_scda.complexity_index,
                problem_difficulty,
                solution_quality
            )
            
            # سعی برای حل مسئله
            success = self.simulated_scda.attempt_solve_problem(
                problem_difficulty,
                solution_quality,
                is_valid
            )
            
            if success:
                results["successful_attempts"] += 1
                results["complexity_gains"].append(self.simulated_scda.complexity_index)
                results["energy_changes"].append(self.simulated_scda.energy)
            
            # ثبت رویداد
            self.current_scenario.add_event("problem_solved", {
                "attempt": i + 1,
                "difficulty": problem_difficulty,
                "quality": solution_quality,
                "success": success,
                "is_valid": is_valid
            })
        
        # ذخیره عکس‌العمل
        self.current_scenario.add_scda_snapshot(self.simulated_scda, num_attempts)
        
        return results
    
    def simulate_breeding(self, parent2: SingleCellDigitalAccount) -> Dict[str, Any]:
        """
        شبیه‌سازی تولید مثل با یک SCDA دیگر
        
        :param parent2: والد دوم
        :return: نتایج شبیه‌سازی
        """
        if not self.current_scenario:
            raise ValueError("No active scenario. Create a scenario first.")
        
        # پیش‌بینی ویژگی‌های فرزند
        predicted_traits = predict_child_traits(self.simulated_scda, parent2)
        
        # ایجاد فرزند
        child = breed_scdas(self.simulated_scda, parent2)
        
        # ثبت رویداد
        self.current_scenario.add_event("breeding", {
            "parent1_id": self.simulated_scda.identity,
            "parent2_id": parent2.identity,
            "child_id": child.identity,
            "predicted_traits": predicted_traits
        })
        
        return {
            "child_id": child.identity,
            "predicted_traits": predicted_traits,
            "child_state": child.get_state()
        }
    
    def simulate_mutation(self, force: bool = False) -> Dict[str, Any]:
        """
        شبیه‌سازی جهش ژنتیکی
        
        :param force: اجبار جهش
        :return: نتایج شبیه‌سازی
        """
        if not self.current_scenario:
            raise ValueError("No active scenario. Create a scenario first.")
        
        from laniakea.intelligence.digital_dna import DNAManager
        
        # جهش DNA
        DNAManager.mutate_dna(self.simulated_scda.dna, force=force)
        
        # ثبت رویداد
        self.current_scenario.add_event("mutation", {
            "force": force,
            "new_diversity": self.simulated_scda.dna.calculate_genetic_diversity()
        })
        
        return {
            "mutation_success": True,
            "new_diversity": self.simulated_scda.dna.calculate_genetic_diversity()
        }
    
    def simulate_passive_evolution(self, time_steps: int) -> Dict[str, Any]:
        """
        شبیه‌سازی تکامل غیرفعال (بدون حل مسئله)
        
        :param time_steps: تعداد گام‌های زمانی
        :return: نتایج شبیه‌سازی
        """
        if not self.current_scenario:
            raise ValueError("No active scenario. Create a scenario first.")
        
        complexity_before = self.simulated_scda.complexity_index
        energy_before = self.simulated_scda.energy
        
        for _ in range(time_steps):
            self.simulated_scda.passive_update()
        
        # ثبت رویداد
        self.current_scenario.add_event("passive_evolution", {
            "time_steps": time_steps,
            "complexity_change": self.simulated_scda.complexity_index - complexity_before,
            "energy_change": self.simulated_scda.energy - energy_before
        })
        
        # ذخیره عکس‌العمل
        self.current_scenario.add_scda_snapshot(self.simulated_scda, time_steps)
        
        return {
            "complexity_change": self.simulated_scda.complexity_index - complexity_before,
            "energy_change": self.simulated_scda.energy - energy_before
        }
    
    def compare_scenarios(self) -> Dict[str, Any]:
        """
        مقایسه تمام سناریوهای شبیه‌سازی شده
        
        :return: خلاصه مقایسه
        """
        comparison = {
            "total_scenarios": len(self.scenarios),
            "scenarios": []
        }
        
        for scenario in self.scenarios:
            comparison["scenarios"].append(scenario.get_summary())
        
        return comparison
    
    def export_scenario(self, scenario_index: int) -> str:
        """
        صادر کردن سناریو به فرمت JSON
        
        :param scenario_index: شاخص سناریو
        :return: JSON string
        """
        if scenario_index >= len(self.scenarios):
            raise ValueError(f"Scenario index {scenario_index} out of range")
        
        scenario = self.scenarios[scenario_index]
        
        export_data = {
            "scenario_name": scenario.scenario_name,
            "description": scenario.description,
            "created_at": scenario.created_at,
            "summary": scenario.get_summary(),
            "snapshots": scenario.scda_snapshots,
            "events": scenario.events
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
