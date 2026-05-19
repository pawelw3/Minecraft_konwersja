package com.maciej916.indreb.common.block.impl.machines.recycler;

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
import com.maciej916.indreb.common.interfaces.entity.ISupportUpgrades;
import com.maciej916.indreb.common.interfaces.entity.ITileSound;
import com.maciej916.indreb.common.recipe.impl.RecyclingRecipe;
import com.maciej916.indreb.common.registries.ModBlockEntities;
import com.maciej916.indreb.common.registries.ModItems;
import com.maciej916.indreb.common.registries.ModRecipeType;
import com.maciej916.indreb.common.registries.ModSounds;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import javax.annotation.Nonnull;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.items.CapabilityItemHandler;
import net.minecraftforge.items.wrapper.RangedWrapper;

public class BlockEntityRecycler extends IndRebBlockEntity implements IEnergyBlock, ISupportUpgrades, ITileSound {
   public static final int INPUT_SLOT = 0;
   public static final int OUTPUT_SLOT = 1;
   public BlockEntityProgress progress = new BlockEntityProgress();
   private boolean active = false;
   private RecyclingRecipe recipe;
   private ItemStack cachedInputStack = ItemStack.f_41583_;
   private final ArrayList<LazyOptional<?>> capabilities = new ArrayList<>(
      Arrays.asList(
         LazyOptional.of(this::getStackHandler),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 0, 1)),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 1, 2))
      )
   );

   public BlockEntityRecycler(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.RECYCLER, pWorldPosition, pBlockState);
      this.createEnergyStorage(0, (Integer)ServerConfig.recycler_energy_capacity.get(), EnergyType.RECEIVE, EnergyTier.BASIC);
   }

   protected Optional<RecyclingRecipe> getRecipe(ItemStack input) {
      return this.f_58857_.m_7465_().m_44015_((RecipeType)ModRecipeType.RECYCLING.get(), new SimpleContainer(new ItemStack[]{input}), this.f_58857_);
   }

   protected ItemStack getRecipeResult(ItemStack stack) {
      return this.recipe.m_5874_(new SimpleContainer(new ItemStack[]{stack}));
   }

   private boolean isValidInput(ItemStack stack) {
      return stack.m_41619_() ? false : this.getRecipe(stack).isPresent();
   }

   private boolean canWork(ItemStack outputStack, ItemStack resultStack) {
      return outputStack.m_41619_() || resultStack.m_41613_() + outputStack.m_41613_() <= outputStack.m_41741_();
   }

   @Override
   public void tickOperate(BlockState state) {
      this.active = false;
      this.getEnergyStorage().updateConsumed(0);
      ItemStack inputStack = this.getStackHandler().getStackInSlot(0);
      ItemStack outputStack = this.getStackHandler().getStackInSlot(1);
      if (this.cachedInputStack.m_41720_() != inputStack.m_41720_()) {
         this.cachedInputStack = inputStack.m_41777_();
         if (inputStack.m_41720_() != Items.f_41852_ && this.getRecipe(inputStack).isPresent()) {
            this.recipe = this.getRecipe(inputStack).get();
         } else {
            this.recipe = null;
         }
      }

      if (this.recipe != null) {
         if (this.progress.getProgress() == -1.0F) {
            this.progress.setData(0.0F, (float)this.recipe.getDuration());
         }

         this.progress.setProgressMax(this.getSpeedFactor() * (float)this.recipe.getDuration());
         int energyCost = (int)((float)this.recipe.getPowerCost() * this.getEnergyUsageFactor());
         ItemStack resultStack = new ItemStack(ModItems.SCRAP);
         if (this.canWork(outputStack, resultStack)) {
            if (this.getEnergyStorage().consumeEnergy(energyCost, true) == energyCost && this.progress.getProgress() <= this.progress.getProgressMax()) {
               this.active = true;
               this.progress.incProgress(1.0F);
               this.getEnergyStorage().consumeEnergy(energyCost, false);
               this.getEnergyStorage().updateConsumed(energyCost);
            }

            if (this.progress.getProgress() >= this.progress.getProgressMax()) {
               inputStack.m_41774_(1);
               this.getStackHandler().setStackInSlot(0, inputStack.m_41777_());
               if (Math.random() <= (double)this.recipe.getChance()) {
                  if (outputStack.m_41619_()) {
                     this.getStackHandler().setStackInSlot(1, resultStack.m_41777_());
                  } else {
                     outputStack.m_41769_(resultStack.m_41613_());
                     this.getStackHandler().setStackInSlot(1, outputStack.m_41777_());
                  }
               }

               this.progress.setBoth(-1.0F);
            }
         }
      } else {
         this.progress.setBoth(-1.0F);
      }

      this.setActive(this.active);
      if (this.progress.changed()) {
         super.updateBlockState();
      }
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
   public boolean canReceiveEnergyDir(Direction side) {
      return true;
   }

   public SoundEvent getSoundEvent() {
      return ModSounds.RECYCLER;
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

   @Nonnull
   @Override
   public <T> LazyOptional<T> getCapability(@Nonnull Capability<T> cap, @Nullable Direction side) {
      if (cap == CapabilityItemHandler.ITEM_HANDLER_CAPABILITY) {
         if (side == null) {
            return this.capabilities.get(0).cast();
         } else {
            return switch (side) {
               case DOWN -> this.capabilities.get(2).cast();
               case UP, NORTH, SOUTH, WEST, EAST -> this.capabilities.get(1).cast();
               default -> throw new IncompatibleClassChangeError();
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
