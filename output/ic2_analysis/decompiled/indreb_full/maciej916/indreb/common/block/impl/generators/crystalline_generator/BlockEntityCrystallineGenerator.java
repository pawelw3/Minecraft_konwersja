package com.maciej916.indreb.common.block.impl.generators.crystalline_generator;

import com.maciej916.indreb.common.config.ServerConfig;
import com.maciej916.indreb.common.energy.interfaces.IEnergyBlock;
import com.maciej916.indreb.common.entity.block.BlockEntityProgress;
import com.maciej916.indreb.common.entity.block.IndRebBlockEntity;
import com.maciej916.indreb.common.entity.slot.IndRebSlot;
import com.maciej916.indreb.common.entity.slot.SlotBattery;
import com.maciej916.indreb.common.enums.EnergyTier;
import com.maciej916.indreb.common.enums.EnergyType;
import com.maciej916.indreb.common.enums.GuiSlotType;
import com.maciej916.indreb.common.enums.InventorySlotType;
import com.maciej916.indreb.common.interfaces.entity.ICooldown;
import com.maciej916.indreb.common.interfaces.entity.IElectricSlot;
import com.maciej916.indreb.common.interfaces.entity.ITileSound;
import com.maciej916.indreb.common.registries.ModBlockEntities;
import com.maciej916.indreb.common.registries.ModSounds;
import java.util.ArrayList;
import java.util.Arrays;
import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.ForgeHooks;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.items.CapabilityItemHandler;
import net.minecraftforge.items.wrapper.RangedWrapper;

public class BlockEntityCrystallineGenerator extends IndRebBlockEntity implements ICooldown, IEnergyBlock, ITileSound {
   public static final int INPUT_SLOT = 0;
   private boolean active = false;
   public BlockEntityProgress progressBurn = new BlockEntityProgress();
   private final ArrayList<LazyOptional<?>> capabilities = new ArrayList<>(
      Arrays.asList(LazyOptional.of(this::getStackHandler), LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 0, 1)))
   );

   public BlockEntityCrystallineGenerator(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.CRYSTALLINE_GENERATOR, pWorldPosition, pBlockState);
      this.createEnergyStorage(0, (Integer)ServerConfig.generator_energy_capacity.get(), EnergyType.EXTRACT, EnergyTier.BASIC);
   }

   @Override
   public ArrayList<IndRebSlot> addInventorySlot(ArrayList<IndRebSlot> slots) {
      slots.add(new IndRebSlot(0, 80, 35, InventorySlotType.INPUT, GuiSlotType.NORMAL, 79, 34));
      return super.addInventorySlot(slots);
   }

   @Override
   public void tickOperate(BlockState state) {
      this.progressBurn.clearChanged();
      this.active = false;
      if (this.getCooldown() == 0) {
         ItemStack inputStack = this.getStackHandler().getStackInSlot(0);
         if (this.getEnergyStorage().generateEnergy((Integer)ServerConfig.generator_tick_generate.get(), true)
            == (Integer)ServerConfig.generator_tick_generate.get()) {
            if (this.progressBurn.getProgress() > 0.0F) {
               this.active = true;
               this.progressBurn.decProgress(1.0F);
               this.getEnergyStorage().generateEnergy((Integer)ServerConfig.generator_tick_generate.get(), false);
            } else {
               this.active = false;
               this.progressBurn.setBoth(-1.0F);
               if (!inputStack.m_41619_()) {
                  int burnTime = ForgeHooks.getBurnTime(inputStack, RecipeType.f_44108_);
                  if (burnTime > 0) {
                     this.progressBurn.setBoth((float)burnTime);
                     inputStack.m_41774_(1);
                     this.active = true;
                  }
               }
            }
         }

         if (this.active
            && this.getEnergyStorage().generateEnergy((Integer)ServerConfig.generator_tick_generate.get(), true)
               < (Integer)ServerConfig.generator_tick_generate.get()
            && this.progressBurn.getProgress() > 0.0F) {
            this.setCooldown(10);
         }
      }

      this.setActive(this.active);
      if (this.progressBurn.changed()) {
         super.updateBlockState();
      }
   }

   @Override
   public boolean isItemValidForSlot(int slot, @Nonnull ItemStack stack) {
      return slot != 0
         ? super.isItemValidForSlot(slot, stack)
         : ForgeHooks.getBurnTime(stack, RecipeType.f_44108_) > 0 && !stack.m_41720_().equals(Items.f_42448_);
   }

   @Override
   public ItemStack insertItemForSlot(int slot, @Nonnull ItemStack stack, boolean simulate) {
      return (slot != 0 || ForgeHooks.getBurnTime(stack, RecipeType.f_44108_) > 0) && !stack.m_41720_().equals(Items.f_42448_)
         ? super.insertItemForSlot(slot, stack, simulate)
         : stack;
   }

   @Override
   public void m_142466_(CompoundTag tag) {
      super.m_142466_(tag);
      this.progressBurn.deserializeNBT(tag.m_128469_("progress"));
      this.active = tag.m_128471_("active");
   }

   @Override
   public CompoundTag save(CompoundTag tag) {
      tag.m_128365_("progress", this.progressBurn.serializeNBT());
      tag.m_128379_("active", this.active);
      return super.save(tag);
   }

   @Override
   protected void m_183515_(CompoundTag tag) {
      super.m_183515_(tag);
      this.save(tag);
   }

   @Override
   public ArrayList<IElectricSlot> addBatterySlot(ArrayList<IElectricSlot> slots) {
      slots.add(new SlotBattery(0, 152, 62, true));
      return super.addBatterySlot(slots);
   }

   public SoundEvent getSoundEvent() {
      return ModSounds.GENERATOR;
   }

   @Override
   public boolean canExtractEnergyDir(Direction side) {
      return true;
   }

   @Nonnull
   @Override
   public <T> LazyOptional<T> getCapability(@Nonnull Capability<T> cap, @Nullable Direction side) {
      return cap == CapabilityItemHandler.ITEM_HANDLER_CAPABILITY ? this.capabilities.get(0).cast() : super.getCapability(cap, side);
   }

   @Override
   public void onBreak() {
      for (LazyOptional<?> capability : this.capabilities) {
         capability.invalidate();
      }

      super.onBreak();
   }
}
