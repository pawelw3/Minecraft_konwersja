package dev.ftb.mods.ftbic.block.entity.generator;

import dev.ftb.mods.ftbic.FTBICConfig;
import dev.ftb.mods.ftbic.block.BurntCableBlock;
import dev.ftb.mods.ftbic.block.CableBlock;
import dev.ftb.mods.ftbic.block.ElectricBlockInstance;
import dev.ftb.mods.ftbic.block.entity.ElectricBlockEntity;
import dev.ftb.mods.ftbic.block.entity.machine.BatteryInventory;
import dev.ftb.mods.ftbic.util.CachedEnergyStorage;
import dev.ftb.mods.ftbic.util.CachedEnergyStorageOrigin;
import dev.ftb.mods.ftbic.util.EnergyHandler;
import dev.ftb.mods.ftbic.util.EnergyItemHandler;
import dev.ftb.mods.ftbic.util.FTBICUtils;
import dev.ftb.mods.ftbic.util.ForgeEnergyHandler;
import java.util.HashSet;
import java.util.Set;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.energy.CapabilityEnergy;
import net.minecraftforge.energy.IEnergyStorage;

public class GeneratorBlockEntity extends ElectricBlockEntity {
   private long currentElectricNetwork = -1L;
   private CachedEnergyStorage[] connectedEnergyBlocks;
   public final BatteryInventory chargeBatteryInventory = new BatteryInventory(this, true);
   public double maxEnergyOutput;
   public double maxEnergyOutputTransfer;

   public GeneratorBlockEntity(ElectricBlockInstance type, BlockPos pos, BlockState state) {
      super(type, pos, state);
   }

   @Override
   public void initProperties() {
      super.initProperties();
      this.maxEnergyOutput = this.electricBlockInstance.maxEnergyOutput;
      this.maxEnergyOutputTransfer = (Double)FTBICConfig.ENERGY.LV_TRANSFER_RATE.get();
   }

   @Override
   public void writeData(CompoundTag tag) {
      super.writeData(tag);
      if (!this.chargeBatteryInventory.getStackInSlot(0).m_41619_()) {
         tag.m_128365_("ChargeBattery", this.chargeBatteryInventory.getStackInSlot(0).serializeNBT());
      }
   }

   @Override
   public void readData(CompoundTag tag) {
      super.readData(tag);
      if (tag.m_128441_("ChargeBattery")) {
         this.chargeBatteryInventory.loadItem(ItemStack.m_41712_(tag.m_128469_("ChargeBattery")));
      } else {
         this.chargeBatteryInventory.loadItem(ItemStack.f_41583_);
      }
   }

   @Override
   public void onBroken(Level level, BlockPos pos) {
      super.onBroken(level, pos);
      Block.m_49840_(level, pos, this.chargeBatteryInventory.getStackInSlot(0));
   }

   public void handleEnergyOutput() {
      if (!this.f_58857_.m_5776_()) {
         if (this.energy > 0.0) {
            ItemStack battery = this.chargeBatteryInventory.getStackInSlot(0);
            if (!battery.m_41619_() && battery.m_41720_() instanceof EnergyItemHandler item) {
               double transfer = item.isCreativeEnergyItem()
                  ? Double.POSITIVE_INFINITY
                  : this.maxEnergyOutputTransfer * (Double)FTBICConfig.MACHINES.ITEM_TRANSFER_EFFICIENCY.get();
               double e = item.insertEnergy(battery, Math.min(this.energy, transfer), false);
               if (e > 0.0) {
                  this.energy -= e;
                  this.active = true;
                  this.m_6596_();
               }
            }
         }

         double tenergy = Math.min(this.energy, this.maxEnergyOutputTransfer);
         if (!(tenergy <= 0.0)) {
            CachedEnergyStorage[] blocks = this.getConnectedEnergyBlocks();
            int validBlocks = 0;

            for (CachedEnergyStorage storage : blocks) {
               if (storage.isInvalid()) {
                  electricNetworkUpdated(this.f_58857_, storage.blockEntity.m_58899_());
               } else if (storage.shouldReceiveEnergy()) {
                  validBlocks++;
               }
            }

            if (validBlocks > 0) {
               double e = tenergy / (double)validBlocks;

               for (CachedEnergyStorage storagex : blocks) {
                  if (!storagex.isInvalid() && storagex.shouldReceiveEnergy()) {
                     if (storagex.origin.cableTier != null && storagex.origin.cableTier.transferRate < e) {
                        this.f_58857_.m_7731_(storagex.origin.cablePos, BurntCableBlock.getBurntCable(this.f_58857_.m_8055_(storagex.origin.cablePos)), 3);
                        this.f_58857_.m_46796_(1502, storagex.origin.cablePos, 0);
                        storagex.origin.cableBurnt = true;
                     } else {
                        double a = storagex.energyHandler.insertEnergy(Math.min(e, this.energy), false);
                        if (a > 0.0) {
                           this.energy -= a;
                           this.active = true;
                           this.m_6596_();
                        }

                        if (this.energy < e) {
                           break;
                        }
                     }
                  }
               }
            }
         }
      }
   }

   public void handleGeneration() {
   }

   @Override
   public void tick() {
      if (!this.f_58857_.m_5776_()) {
         this.handleGeneration();
      }

      this.handleEnergyOutput();
      this.handleChanges();
   }

   public boolean isValidEnergyOutputSide(Direction direction) {
      return true;
   }

   public boolean isValidEnergyInputSide(Direction direction) {
      return false;
   }

   public CachedEnergyStorage[] getConnectedEnergyBlocks() {
      if (this.f_58857_ != null && !this.f_58857_.m_5776_()) {
         long currentId = getCurrentElectricNetwork(this.f_58857_, this.m_58899_());
         if (this.connectedEnergyBlocks == null || this.currentElectricNetwork == -1L || this.currentElectricNetwork != currentId) {
            Set<CachedEnergyStorage> set = new HashSet<>();
            Set<BlockPos> traversed = new HashSet<>();
            traversed.add(this.f_58858_);

            for (Direction direction : FTBICUtils.DIRECTIONS) {
               if (this.isValidEnergyOutputSide(direction)) {
                  CachedEnergyStorageOrigin origin = new CachedEnergyStorageOrigin();
                  origin.direction = direction;
                  this.find(traversed, set, origin, 0, this.f_58858_, direction);
               }
            }

            this.connectedEnergyBlocks = set.toArray(CachedEnergyStorage.EMPTY);
            this.currentElectricNetwork = currentId;
         }

         return this.connectedEnergyBlocks;
      } else {
         return CachedEnergyStorage.EMPTY;
      }
   }

   private void find(
      Set<BlockPos> traversed, Set<CachedEnergyStorage> set, CachedEnergyStorageOrigin origin, int distance, BlockPos currentPos, Direction direction
   ) {
      if (this.f_58857_ != null && distance <= (Integer)FTBICConfig.ENERGY.MAX_CABLE_LENGTH.get()) {
         BlockPos pos = currentPos.m_142300_(direction);
         if (traversed.add(pos)) {
            BlockState state = this.f_58857_.m_8055_(pos);
            if (state.m_60734_() instanceof CableBlock cableBlock) {
               if (origin.cableTier == null || cableBlock.tier.transferRate < origin.cableTier.transferRate) {
                  origin.cableTier = cableBlock.tier;
                  origin.cablePos = pos;
               }

               for (Direction dir : FTBICUtils.DIRECTIONS) {
                  if ((Boolean)state.m_61143_(CableBlock.CONNECTION[dir.m_122411_()])) {
                     this.find(traversed, set, origin, distance + 1, pos, dir);
                  }
               }
            } else if (state.m_155947_()) {
               BlockEntity entity = this.f_58857_.m_7702_(pos);
               EnergyHandler handler = entity instanceof EnergyHandler ? (EnergyHandler)entity : null;
               if (handler != null) {
                  if (handler != this && handler.getMaxInputEnergy() > 0.0 && !handler.isBurnt() && handler.isValidEnergyInputSide(direction.m_122424_())) {
                     CachedEnergyStorage s = new CachedEnergyStorage();
                     s.origin = origin;
                     s.distance = distance;
                     s.blockEntity = entity;
                     s.energyHandler = handler;
                     set.add(s);
                  }
               } else if ((Double)FTBICConfig.ENERGY.ZAP_TO_FE_CONVERSION_RATE.get() > 0.0) {
                  if (entity == null) {
                     return;
                  }

                  LazyOptional<IEnergyStorage> energyCap = entity.getCapability(CapabilityEnergy.ENERGY, direction.m_122424_());
                  IEnergyStorage feStorage = (IEnergyStorage)energyCap.orElse(null);
                  if (feStorage != null && feStorage.canReceive()) {
                     CachedEnergyStorage s = new CachedEnergyStorage();
                     s.origin = origin;
                     s.distance = distance;
                     s.blockEntity = entity;
                     s.energyHandler = new ForgeEnergyHandler(energyCap, feStorage);
                     set.add(s);
                  }
               }
            }
         }
      }
   }
}
