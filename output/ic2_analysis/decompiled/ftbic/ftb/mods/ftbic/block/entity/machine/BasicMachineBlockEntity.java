package dev.ftb.mods.ftbic.block.entity.machine;

import dev.ftb.mods.ftbic.FTBICConfig;
import dev.ftb.mods.ftbic.block.ElectricBlockInstance;
import dev.ftb.mods.ftbic.block.entity.ElectricBlockEntity;
import dev.ftb.mods.ftbic.item.FTBICItems;
import dev.ftb.mods.ftbic.util.EnergyItemHandler;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.state.BlockState;

public abstract class BasicMachineBlockEntity extends ElectricBlockEntity {
   public final UpgradeInventory upgradeInventory = new UpgradeInventory(this, 4, (Integer)FTBICConfig.MACHINES.UPGRADE_LIMIT_PER_SLOT.get());
   public final BatteryInventory batteryInventory = new BatteryInventory(this, false);
   public double energyUse;
   public double progressSpeed;

   public BasicMachineBlockEntity(ElectricBlockInstance type, BlockPos pos, BlockState state) {
      super(type, pos, state);
   }

   @Override
   public void writeData(CompoundTag tag) {
      super.writeData(tag);
      tag.m_128365_("Upgrades", this.upgradeInventory.serializeNBT().m_128437_("Items", 10));
      if (!this.batteryInventory.getStackInSlot(0).m_41619_()) {
         tag.m_128365_("Battery", this.batteryInventory.getStackInSlot(0).serializeNBT());
      }
   }

   @Override
   public void readData(CompoundTag tag) {
      super.readData(tag);
      CompoundTag tag1 = new CompoundTag();
      tag1.m_128365_("Items", tag.m_128437_("Upgrades", 10));
      this.upgradeInventory.deserializeNBT(tag1);
      if (tag.m_128441_("Battery")) {
         this.batteryInventory.loadItem(ItemStack.m_41712_(tag.m_128469_("Battery")));
      } else {
         this.batteryInventory.loadItem(ItemStack.f_41583_);
      }
   }

   @Override
   public void tick() {
      if (!this.isBurnt() && !this.f_58857_.m_5776_() && this.energy < this.energyCapacity) {
         ItemStack battery = this.batteryInventory.getStackInSlot(0);
         if (!battery.m_41619_() && battery.m_41720_() instanceof EnergyItemHandler item) {
            double transfer = item.isCreativeEnergyItem()
               ? Double.POSITIVE_INFINITY
               : this.maxInputEnergy * (Double)FTBICConfig.MACHINES.ITEM_TRANSFER_EFFICIENCY.get();
            double e = item.extractEnergy(battery, Math.min(this.energyCapacity - this.energy, transfer), false);
            if (e > 0.0) {
               this.energy += e;
               if (battery.m_41619_()) {
                  this.batteryInventory.setStackInSlot(0, ItemStack.f_41583_);
               }

               this.m_6596_();
            }
         }
      }

      this.handleProcessing();
      this.handleChanges();
   }

   @Override
   public double getTotalPossibleEnergyCapacity() {
      return super.getTotalPossibleEnergyCapacity()
         + (double)(
               this.upgradeInventory.getSlots()
                  * Math.min((Integer)FTBICConfig.MACHINES.UPGRADE_LIMIT_PER_SLOT.get(), ((Item)FTBICItems.ENERGY_STORAGE_UPGRADE.get()).m_41459_())
            )
            * (Double)FTBICConfig.MACHINES.STORAGE_UPGRADE.get();
   }

   public void handleProcessing() {
   }

   @Override
   public void onBroken(Level level, BlockPos pos) {
      super.onBroken(level, pos);

      for (int i = 0; i < this.upgradeInventory.getSlots(); i++) {
         Block.m_49840_(level, pos, this.upgradeInventory.getStackInSlot(i));
      }

      Block.m_49840_(level, pos, this.batteryInventory.getStackInSlot(0));
   }

   @Override
   public void initProperties() {
      super.initProperties();
      this.energyUse = this.electricBlockInstance.energyUsage;
      this.progressSpeed = 1.0;
      this.autoEject = false;
   }

   @Override
   public void upgradesChanged() {
      super.upgradesChanged();
      int overclockers = this.upgradeInventory.countUpgrades((Item)FTBICItems.OVERCLOCKER_UPGRADE.get());

      for (int i = 0; i < overclockers; i++) {
         this.energyUse = this.energyUse * (Double)FTBICConfig.MACHINES.OVERCLOCKER_ENERGY_USE.get();
         this.progressSpeed = this.progressSpeed * (Double)FTBICConfig.MACHINES.OVERCLOCKER_SPEED.get();
      }

      for (int transformers = this.upgradeInventory.countUpgrades((Item)FTBICItems.TRANSFORMER_UPGRADE.get()); transformers > 0; this.maxInputEnergy *= 4.0) {
         transformers--;
      }

      if (this.maxInputEnergy > (Double)FTBICConfig.ENERGY.IV_TRANSFER_RATE.get()) {
         this.maxInputEnergy = (Double)FTBICConfig.ENERGY.IV_TRANSFER_RATE.get();
      }

      this.energyCapacity = this.energyCapacity
         + (double)this.upgradeInventory.countUpgrades((Item)FTBICItems.ENERGY_STORAGE_UPGRADE.get()) * (Double)FTBICConfig.MACHINES.STORAGE_UPGRADE.get();
      if (this.energy > this.energyCapacity) {
         this.energy = this.energyCapacity;
      }

      this.autoEject = this.upgradeInventory.countUpgrades((Item)FTBICItems.EJECTOR_UPGRADE.get()) > 0;
   }
}
