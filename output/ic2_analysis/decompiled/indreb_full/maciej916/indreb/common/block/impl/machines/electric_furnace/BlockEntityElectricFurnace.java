package com.maciej916.indreb.common.block.impl.machines.electric_furnace;

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
import com.maciej916.indreb.common.enums.UpgradeType;
import com.maciej916.indreb.common.interfaces.entity.IElectricSlot;
import com.maciej916.indreb.common.interfaces.entity.IExpCollector;
import com.maciej916.indreb.common.interfaces.entity.ISupportUpgrades;
import com.maciej916.indreb.common.registries.ModBlockEntities;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.item.crafting.SmeltingRecipe;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.items.CapabilityItemHandler;
import net.minecraftforge.items.wrapper.RangedWrapper;

public class BlockEntityElectricFurnace extends IndRebBlockEntity implements IEnergyBlock, IExpCollector, ISupportUpgrades {
   public static final int INPUT_SLOT = 0;
   public static final int OUTPUT_SLOT = 1;
   public BlockEntityProgress progress = new BlockEntityProgress();
   private boolean active = false;
   private ItemStack cachedInputStack = ItemStack.f_41583_;
   private ItemStack resultStack = ItemStack.f_41583_;
   private SmeltingRecipe furnaceRecipe;
   ArrayList<LazyOptional<?>> capabilities = new ArrayList<>(
      Arrays.asList(
         LazyOptional.of(this::getStackHandler),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 0, 1)),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 1, 2))
      )
   );

   public BlockEntityElectricFurnace(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.ELECTRIC_FURNACE, pWorldPosition, pBlockState);
      this.createEnergyStorage(0, (Integer)ServerConfig.electric_furnace_energy_capacity.get(), EnergyType.RECEIVE, EnergyTier.BASIC);
   }

   protected Optional<SmeltingRecipe> getRecipe(ItemStack input) {
      return this.f_58857_.m_7465_().m_44015_(RecipeType.f_44108_, new SimpleContainer(new ItemStack[]{input}), this.f_58857_);
   }

   protected ItemStack getRecipeResult(ItemStack stack) {
      return this.furnaceRecipe.m_5874_(new SimpleContainer(new ItemStack[]{stack}));
   }

   private boolean canSmelt(ItemStack inputStack, ItemStack outputStack, ItemStack resultStack) {
      return !inputStack.m_41619_()
         && outputStack.m_41613_() < outputStack.m_41741_()
         && (resultStack.m_41720_() == outputStack.m_41720_() || outputStack.m_41619_());
   }

   private int getSmeltTime() {
      return this.furnaceRecipe.m_43753_();
   }

   private boolean isValidInput(ItemStack stack) {
      return stack.m_41619_() ? false : this.getRecipe(stack).isPresent();
   }

   @Override
   public void tickOperate(BlockState state) {
      this.progress.clearChanged();
      this.active = false;
      this.getEnergyStorage().updateConsumed(0);
      ItemStack inputStack = this.getStackHandler().getStackInSlot(0);
      ItemStack outputStack = this.getStackHandler().getStackInSlot(1);
      if (this.cachedInputStack.m_41720_() != inputStack.m_41720_()) {
         this.cachedInputStack = inputStack.m_41777_();
         if (inputStack.m_41720_() != Items.f_41852_ && this.getRecipe(inputStack).isPresent()) {
            this.furnaceRecipe = this.getRecipe(this.cachedInputStack).orElseThrow();
            this.resultStack = this.getRecipeResult(inputStack);
         } else {
            this.furnaceRecipe = null;
         }
      }

      if (this.furnaceRecipe != null) {
         if (this.canSmelt(inputStack, outputStack, this.resultStack) && this.progress.getProgress() != -1.0F) {
            this.progress.setProgressMax(this.getSpeedFactor() * (float)this.furnaceRecipe.m_43753_());
            int energyCost = (int)((float)((Integer)ServerConfig.electric_furnace_tick_usage.get()).intValue() * this.getEnergyUsageFactor());
            if (this.getEnergyStorage().consumeEnergy(energyCost, true) == energyCost) {
               this.active = true;
               this.progress.incProgress(1.0F);
               this.getEnergyStorage().consumeEnergy(energyCost, false);
               this.getEnergyStorage().updateConsumed(energyCost);
            }

            if (this.progress.getProgress() >= this.progress.getProgressMax()) {
               if (outputStack.m_41619_()) {
                  this.getStackHandler().setStackInSlot(1, this.resultStack.m_41777_());
               } else {
                  outputStack.m_41769_(1);
                  this.getStackHandler().setStackInSlot(1, outputStack.m_41777_());
               }

               inputStack.m_41774_(1);
               this.getStackHandler().setStackInSlot(0, inputStack.m_41777_());
               this.setRecipeUsed(this.furnaceRecipe);
               this.progress.setProgress(-1.0F);
            }
         }
      } else {
         this.progress.setBoth(-1.0F);
      }

      if (this.progress.getProgress() == -1.0F && this.canSmelt(inputStack, outputStack, this.resultStack)) {
         this.progress.setData(0.0F, (float)((int)((double)this.getSmeltTime() * 0.7)));
      }

      this.setActive(this.active);
      if (this.progress.changed()) {
         super.updateBlockState();
      }
   }

   @Override
   public boolean isItemValidForSlot(int slot, @Nonnull ItemStack stack) {
      return slot == 0 ? this.isValidInput(stack) : false;
   }

   @Override
   public ItemStack insertItemForSlot(int slot, @Nonnull ItemStack stack, boolean simulate) {
      return slot == 0 && !this.isValidInput(stack) ? stack : super.insertItemForSlot(slot, stack, simulate);
   }

   @Override
   public void m_142466_(CompoundTag tag) {
      super.m_142466_(tag);
      this.active = tag.m_128471_("active");
      this.progress.deserializeNBT(tag.m_128469_("progress"));
   }

   @Override
   public CompoundTag save(CompoundTag tag) {
      tag.m_128379_("active", this.active);
      tag.m_128365_("progress", this.progress.serializeNBT());
      return super.save(tag);
   }

   @Override
   public ArrayList<IndRebSlot> addInventorySlot(ArrayList<IndRebSlot> slots) {
      slots.add(new IndRebSlot(0, 48, 35, InventorySlotType.INPUT, GuiSlotType.NORMAL, 47, 34));
      slots.add(new IndRebSlot(1, 108, 35, InventorySlotType.OUTPUT, GuiSlotType.LARGE, 103, 30));
      return super.addInventorySlot(slots);
   }

   @Override
   public ArrayList<IElectricSlot> addBatterySlot(ArrayList<IElectricSlot> slots) {
      slots.add(new SlotBattery(0, 152, 62, false));
      return super.addBatterySlot(slots);
   }

   @Override
   public float getExperience(Recipe<?> recipe) {
      return ((SmeltingRecipe)recipe).m_43750_();
   }

   @Override
   public boolean canReceiveEnergyDir(Direction side) {
      return true;
   }

   @Nonnull
   @Override
   public <T> LazyOptional<T> getCapability(@Nonnull Capability<T> cap, @Nullable Direction side) {
      if (cap == CapabilityItemHandler.ITEM_HANDLER_CAPABILITY) {
         if (side == null) {
            return this.capabilities.get(0).cast();
         } else {
            return switch (side) {
               case UP -> this.capabilities.get(1).cast();
               case DOWN -> this.capabilities.get(2).cast();
               default -> this.capabilities.get(0).cast();
            };
         }
      } else {
         return super.getCapability(cap, side);
      }
   }

   @Override
   public void onBreak() {
      for (LazyOptional<?> capability : this.capabilities) {
         capability.invalidate();
      }

      super.onBreak();
   }

   @Override
   public List<UpgradeType> getSupportedUpgrades() {
      return List.of(
         UpgradeType.OVERCLOCKER,
         UpgradeType.TRANSFORMER,
         UpgradeType.ENERGY_STORAGE,
         UpgradeType.EJECTOR,
         UpgradeType.PULLING,
         UpgradeType.REDSTONE_SIGNAL_INVERTER
      );
   }
}
