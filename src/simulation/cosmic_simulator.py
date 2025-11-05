"""
Laniakea Protocol - Cosmic Simulator
شبیه‌ساز کیهانی با قوانین فیزیکی و تکامل
"""

import random
import math
from typing import List, Dict, Any, Optional, Tuple
from src.core.models import CosmicCell, ValueVector


class PhysicsEngine:
    """
    موتور فیزیک برای شبیه‌سازی
    """

    def __init__(self):
        self.gravity_constant = 6.67430e-11  # ثابت گرانش
        self.speed_of_light = 299792458  # سرعت نور (m/s)
        self.planck_constant = 6.62607015e-34  # ثابت پلانک

        # پارامترهای قابل تنظیم
        self.time_scale = 1.0
        self.energy_decay_rate = 0.01
        self.knowledge_diffusion_rate = 0.1

    def calculate_force(self, cell1: CosmicCell, cell2: CosmicCell) -> Tuple[float, float, float]:
        """
        محاسبه نیروی بین دو سلول

        Returns:
            (fx, fy, fz) نیرو در سه بُعد
        """
        # محاسبه فاصله
        dx = cell2.position[0] - cell1.position[0]
        dy = cell2.position[1] - cell1.position[1]
        dz = cell2.position[2] - cell1.position[2]

        distance = math.sqrt(dx**2 + dy**2 + dz**2)

        if distance < 0.001:  # جلوگیری از تقسیم بر صفر
            return (0.0, 0.0, 0.0)

        # نیروی جاذبه (بر اساس انرژی به جای جرم)
        force_magnitude = (cell1.energy * cell2.energy) / (distance**2)

        # نرمال‌سازی
        fx = force_magnitude * (dx / distance)
        fy = force_magnitude * (dy / distance)
        fz = force_magnitude * (dz / distance)

        return (fx, fy, fz)

    def update_position(self, cell: CosmicCell, dt: float):
        """
        به‌روزرسانی موقعیت سلول

        Args:
            cell: سلول
            dt: گام زمانی
        """
        # به‌روزرسانی موقعیت بر اساس سرعت
        new_x = cell.position[0] + cell.velocity[0] * dt
        new_y = cell.position[1] + cell.velocity[1] * dt
        new_z = cell.position[2] + cell.velocity[2] * dt

        cell.position = (new_x, new_y, new_z)

    def apply_force(self, cell: CosmicCell, force: Tuple[float, float, float], dt: float):
        """
        اعمال نیرو به سلول

        Args:
            cell: سلول
            force: نیرو (fx, fy, fz)
            dt: گام زمانی
        """
        # F = ma => a = F/m (اینجا از انرژی به عنوان جرم استفاده می‌کنیم)
        if cell.energy > 0:
            ax = force[0] / cell.energy
            ay = force[1] / cell.energy
            az = force[2] / cell.energy

            # به‌روزرسانی سرعت
            new_vx = cell.velocity[0] + ax * dt
            new_vy = cell.velocity[1] + ay * dt
            new_vz = cell.velocity[2] + az * dt

            # محدودیت سرعت (نمی‌تواند از سرعت نور بیشتر شود)
            speed = math.sqrt(new_vx**2 + new_vy**2 + new_vz**2)
            max_speed = self.speed_of_light * 0.1  # 10% سرعت نور

            if speed > max_speed:
                scale = max_speed / speed
                new_vx *= scale
                new_vy *= scale
                new_vz *= scale

            cell.velocity = (new_vx, new_vy, new_vz)

    def decay_energy(self, cell: CosmicCell, dt: float):
        """
        کاهش انرژی سلول در طول زمان

        Args:
            cell: سلول
            dt: گام زمانی
        """
        decay = cell.energy * self.energy_decay_rate * dt
        cell.energy = max(0.0, cell.energy - decay)

        if cell.energy <= 0:
            cell.state = "dead"


class EvolutionEngine:
    """
    موتور تکامل برای سلول‌ها
    """

    def __init__(self):
        self.mutation_rate = 0.01
        self.reproduction_threshold = 200.0  # حداقل انرژی برای تکثیر
        self.reproduction_cost = 100.0  # هزینه انرژی تکثیر

    def can_reproduce(self, cell: CosmicCell) -> bool:
        """
        بررسی امکان تکثیر

        Args:
            cell: سلول

        Returns:
            True اگر بتواند تکثیر کند
        """
        return (
            cell.state == "alive"
            and cell.energy >= self.reproduction_threshold
            and cell.knowledge >= 10.0
        )

    def reproduce(self, parent: CosmicCell) -> Optional[CosmicCell]:
        """
        تکثیر سلول

        Args:
            parent: سلول والد

        Returns:
            سلول فرزند
        """
        if not self.can_reproduce(parent):
            return None

        # کاهش انرژی والد
        parent.energy -= self.reproduction_cost

        # ایجاد فرزند
        import hashlib
        from time import time

        child_id = hashlib.sha256(f"{parent.id}{time()}".encode()).hexdigest()

        # وراثت ژنوم با جهش
        child_genome = self._mutate_genome(parent.genome.copy())

        # موقعیت نزدیک والد
        offset = random.uniform(-1.0, 1.0)
        child_position = (
            parent.position[0] + offset,
            parent.position[1] + offset,
            parent.position[2] + offset,
        )

        child = CosmicCell(
            id=child_id,
            generation=parent.generation + 1,
            energy=self.reproduction_cost * 0.5,  # نصف انرژی صرف شده
            knowledge=parent.knowledge * 0.3,  # 30% دانش والد
            position=child_position,
            velocity=(0.0, 0.0, 0.0),
            genome=child_genome,
            state="alive",
        )

        print(f"👶 Cell reproduced: Gen {child.generation}")
        return child

    def _mutate_genome(self, genome: Dict[str, Any]) -> Dict[str, Any]:
        """
        جهش ژنوم

        Args:
            genome: ژنوم والد

        Returns:
            ژنوم جهش یافته
        """
        mutated = genome.copy()

        # جهش تصادفی
        if random.random() < self.mutation_rate:
            # افزودن یا تغییر یک ژن
            gene_name = f"gene_{random.randint(1, 100)}"
            gene_value = random.uniform(0.0, 1.0)
            mutated[gene_name] = gene_value

        return mutated

    def evolve_cell(self, cell: CosmicCell, environment: Dict[str, Any]):
        """
        تکامل سلول بر اساس محیط

        Args:
            cell: سلول
            environment: محیط
        """
        # افزایش دانش بر اساس محیط
        knowledge_gain = environment.get("knowledge_density", 0.1)
        cell.knowledge += knowledge_gain

        # تطبیق با محیط
        if "temperature" in environment:
            temp = environment["temperature"]
            # سلول‌ها در دمای مناسب بهتر رشد می‌کنند
            if 0.3 <= temp <= 0.7:
                cell.energy += 1.0


class CosmicSimulator:
    """
    شبیه‌ساز کیهانی کامل
    """

    def __init__(self):
        self.physics = PhysicsEngine()
        self.evolution = EvolutionEngine()
        self.cells: List[CosmicCell] = []
        self.time = 0.0
        self.dt = 0.1  # گام زمانی
        self.environment = {"temperature": 0.5, "knowledge_density": 0.1, "energy_field": 1.0}

        print("🌌 Cosmic Simulator initialized")

    def create_genesis_cell(self) -> CosmicCell:
        """
        ایجاد تک‌سلولی اولیه (پیدایش)

        Returns:
            سلول پیدایش
        """
        import hashlib
        from time import time

        genesis_id = hashlib.sha256(f"genesis{time()}".encode()).hexdigest()

        genesis_cell = CosmicCell(
            id=genesis_id,
            generation=0,
            energy=100.0,
            knowledge=1.0,
            position=(0.0, 0.0, 0.0),
            velocity=(0.0, 0.0, 0.0),
            genome={"curiosity": 1.0, "adaptability": 0.8, "efficiency": 0.6},
            state="alive",
        )

        self.cells.append(genesis_cell)
        print(f"🌱 Genesis cell created: {genesis_id[:8]}")
        return genesis_cell

    def step(self):
        """
        یک گام شبیه‌سازی
        """
        self.time += self.dt

        # به‌روزرسانی فیزیک
        self._update_physics()

        # به‌روزرسانی تکامل
        self._update_evolution()

        # حذف سلول‌های مرده
        self._cleanup_dead_cells()

        # به‌روزرسانی محیط
        self._update_environment()

    def _update_physics(self):
        """به‌روزرسانی فیزیک تمام سلول‌ها"""
        # محاسبه نیروها
        forces = {cell.id: (0.0, 0.0, 0.0) for cell in self.cells}

        for i, cell1 in enumerate(self.cells):
            for cell2 in self.cells[i + 1 :]:
                force = self.physics.calculate_force(cell1, cell2)

                # نیروی عکس‌العمل
                forces[cell1.id] = tuple(forces[cell1.id][j] + force[j] for j in range(3))
                forces[cell2.id] = tuple(forces[cell2.id][j] - force[j] for j in range(3))

        # اعمال نیروها و به‌روزرسانی موقعیت‌ها
        for cell in self.cells:
            if cell.state == "alive":
                self.physics.apply_force(cell, forces[cell.id], self.dt)
                self.physics.update_position(cell, self.dt)
                self.physics.decay_energy(cell, self.dt)

    def _update_evolution(self):
        """به‌روزرسانی تکامل"""
        new_cells = []

        for cell in self.cells:
            if cell.state == "alive":
                # تکامل سلول
                self.evolution.evolve_cell(cell, self.environment)

                # تکثیر
                child = self.evolution.reproduce(cell)
                if child:
                    new_cells.append(child)

        # افزودن سلول‌های جدید
        self.cells.extend(new_cells)

    def _cleanup_dead_cells(self):
        """حذف سلول‌های مرده"""
        alive_cells = [cell for cell in self.cells if cell.state == "alive"]
        dead_count = len(self.cells) - len(alive_cells)

        if dead_count > 0:
            print(f"💀 {dead_count} cells died")

        self.cells = alive_cells

    def _update_environment(self):
        """به‌روزرسانی محیط"""
        # دانش کل سلول‌ها تأثیر بر محیط دارد
        if self.cells:
            total_knowledge = sum(cell.knowledge for cell in self.cells)
            self.environment["knowledge_density"] = total_knowledge / len(self.cells) * 0.01

    def run(self, steps: int):
        """
        اجرای شبیه‌سازی برای تعداد مشخصی گام

        Args:
            steps: تعداد گام‌ها
        """
        print(f"🚀 Running simulation for {steps} steps...")

        for i in range(steps):
            self.step()

            # گزارش هر 100 گام
            if (i + 1) % 100 == 0:
                stats = self.get_stats()
                print(
                    f"Step {i+1}: {stats['alive_cells']} cells, "
                    f"Total knowledge: {stats['total_knowledge']:.2f}, "
                    f"Avg energy: {stats['avg_energy']:.2f}"
                )

    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار شبیه‌سازی"""
        if not self.cells:
            return {
                "time": self.time,
                "alive_cells": 0,
                "total_knowledge": 0.0,
                "avg_energy": 0.0,
                "max_generation": 0,
            }

        return {
            "time": self.time,
            "alive_cells": len(self.cells),
            "total_knowledge": sum(cell.knowledge for cell in self.cells),
            "avg_energy": sum(cell.energy for cell in self.cells) / len(self.cells),
            "max_generation": max(cell.generation for cell in self.cells),
            "environment": self.environment,
        }

    def visualize_state(self) -> str:
        """
        نمایش وضعیت فعلی به صورت متنی

        Returns:
            نمایش متنی
        """
        output = [
            "=" * 60,
            f"🌌 COSMIC SIMULATION - Time: {self.time:.2f}",
            "=" * 60,
            f"Alive Cells: {len(self.cells)}",
            f"Environment: {self.environment}",
            "",
            "Top 5 Cells:",
            "-" * 60,
        ]

        # مرتب‌سازی بر اساس دانش
        sorted_cells = sorted(self.cells, key=lambda c: c.knowledge, reverse=True)[:5]

        for i, cell in enumerate(sorted_cells, 1):
            output.append(
                f"{i}. Gen {cell.generation} | "
                f"Energy: {cell.energy:.2f} | "
                f"Knowledge: {cell.knowledge:.2f} | "
                f"Pos: ({cell.position[0]:.2f}, {cell.position[1]:.2f}, {cell.position[2]:.2f})"
            )

        output.append("=" * 60)
        return "\n".join(output)
