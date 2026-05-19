package com.maciej916.indreb.common.block.impl.machines.canning_machine;

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
import com.maciej916.indreb.common.interfaces.entity.ITileSound;
import com.maciej916.indreb.common.recipe.impl.CanningRecipe;
import com.maciej916.indreb.common.registries.ModBlockEntities;
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
import net.minecraft.world.item.crafting.Recipe;
import net.minecraft.world.item.crafting.RecipeType;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.items.CapabilityItemHandler;
import net.minecraftforge.items.wrapper.RangedWrapper;

public class BlockEntityCanningMachine extends IndRebBlockEntity implements IEnergyBlock, IExpCollector, ISupportUpgrades, ITileSound {
   public static final int INPUT_SLOT_0 = 0;
   public static final int INPUT_SLOT_1 = 1;
   public static final int OUTPUT_SLOT = 2;
   public BlockEntityProgress progress = new BlockEntityProgress();
   private CanningRecipe recipe;
   private boolean active = false;
   private ItemStack cachedInputStack0 = ItemStack.f_41583_;
   private ItemStack cachedInputStack1 = ItemStack.f_41583_;
   private final ArrayList<LazyOptional<?>> capabilities = new ArrayList<>(
      Arrays.asList(
         LazyOptional.of(this::getStackHandler),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 0, 2)),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 2, 3))
      )
   );

   public BlockEntityCanningMachine(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.CANNING_MACHINE, pWorldPosition, pBlockState);
      this.createEnergyStorage(0, (Integer)ServerConfig.canning_machine_energy_capacity.get(), EnergyType.RECEIVE, EnergyTier.BASIC);
   }

   @Override
   public ArrayList<IndRebSlot> addInventorySlot(ArrayList<IndRebSlot> slots) {
      slots.add(new IndRebSlot(0, 8, 35, InventorySlotType.INPUT, GuiSlotType.NORMAL, 7, 34));
      slots.add(new IndRebSlot(1, 46, 35, InventorySlotType.INPUT, GuiSlotType.NORMAL, 45, 34));
      slots.add(new IndRebSlot(2, 121, 35, InventorySlotType.OUTPUT, GuiSlotType.LARGE, 116, 30));
      return super.addInventorySlot(slots);
   }

   @Override
   public ArrayList<IElectricSlot> addBatterySlot(ArrayList<IElectricSlot> slots) {
      slots.add(new SlotBattery(0, 152, 62, false));
      return super.addBatterySlot(slots);
   }

   protected Optional<CanningRecipe> getRecipe(ItemStack... input) {
      return this.f_58857_.m_7465_().m_44015_((RecipeType)ModRecipeType.CANNING.get(), new SimpleContainer(input), this.f_58857_);
   }

   protected ItemStack getRecipeResult(ItemStack stack) {
      return this.recipe.m_5874_(new SimpleContainer(new ItemStack[]{stack}));
   }

   private boolean isValidInput(ItemStack stack, int slot) {
      if (stack.m_41619_()) {
         return false;
      } else {
         Optional<CanningRecipe> recipe = this.getRecipe(stack);
         if (recipe.isPresent()) {
            return slot == 0
               ? recipe.get().getFirstIngredient().m_43908_()[0].m_41720_() == stack.m_41720_()
               : recipe.get().getSecondIngredient().m_43908_()[0].m_41720_() == stack.m_41720_();
         } else {
            return false;
         }
      }
   }

   private boolean canWork(ItemStack outputStack, ItemStack resultStack) {
      return outputStack.m_41619_() || resultStack.m_41613_() + outputStack.m_41613_() <= outputStack.m_41741_();
   }

   @Override
   public void tickOperate(BlockState state) {
      this.active = false;
      this.getEnergyStorage().updateConsumed(0);
      ItemStack inputStack0 = this.getStackHandler().getStackInSlot(0);
      ItemStack inputStack1 = this.getStackHandler().getStackInSlot(1);
      ItemStack outputStack = this.getStackHandler().getStackInSlot(2);
      if (this.cachedInputStack0.m_41720_() != inputStack0.m_41720_() || this.cachedInputStack1.m_41720_() != inputStack1.m_41720_()) {
         this.cachedInputStack0 = inputStack0.m_41777_();
         this.cachedInputStack1 = inputStack1.m_41777_();
         if (this.getRecipe(inputStack0, inputStack1).isPresent()) {
            this.recipe = this.getRecipe(inputStack0, inputStack1).get();
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
         if (this.canWork(outputStack, this.recipe.m_8043_())) {
            if (this.getEnergyStorage().consumeEnergy(energyCost, true) == energyCost && this.progress.getProgress() <= this.progress.getProgressMax()) {
               this.active = true;
               this.progress.incProgress(1.0F);
               this.getEnergyStorage().consumeEnergy(energyCost, false);
               this.getEnergyStorage().updateConsumed(energyCost);
            }

            if (this.progress.getProgress() >= this.progress.getProgressMax()) {
               inputStack0.m_41774_(this.recipe.getFirstIngredientCount());
               this.getStackHandler().setStackInSlot(0, inputStack0.m_41777_());
               inputStack1.m_41774_(this.recipe.getSecondIngredientCount());
               this.getStackHandler().setStackInSlot(1, inputStack1.m_41777_());
               if (outputStack.m_41619_()) {
                  this.getStackHandler().setStackInSlot(2, this.recipe.m_8043_().m_41777_());
               } else {
                  outputStack.m_41769_(this.recipe.m_8043_().m_41613_());
                  this.getStackHandler().setStackInSlot(2, outputStack.m_41777_());
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
   public boolean isItemValidForSlot(int slot, @Nonnull ItemStack stack) {
      if (slot == 0) {
         return this.isValidInput(stack, slot);
      } else {
         return slot == 1 ? this.isValidInput(stack, slot) : false;
      }
   }

   @Override
   public ItemStack insertItemForSlot(int slot, @Nonnull ItemStack stack, boolean simulate) {
      if (slot == 0 && !this.isValidInput(stack, slot)) {
         return stack;
      } else {
         return slot == 1 && !this.isValidInput(stack, slot) ? stack : super.insertItemForSlot(slot, stack, simulate);
      }
   }

   @Override
   public boolean canReceiveEnergyDir(Direction side) {
      return true;
   }

   @Override
   public float getExperience(Recipe<?> recipe) {
      return ((CanningRecipe)recipe).getExperience();
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

   public SoundEvent getSoundEvent() {
      return ModSounds.CANNING_MACHINE;
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
