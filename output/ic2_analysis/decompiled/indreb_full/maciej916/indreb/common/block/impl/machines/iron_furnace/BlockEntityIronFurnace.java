package com.maciej916.indreb.common.block.impl.machines.iron_furnace;

import com.maciej916.indreb.common.entity.block.BlockEntityProgress;
import com.maciej916.indreb.common.entity.block.IndRebBlockEntity;
import com.maciej916.indreb.common.entity.slot.IndRebSlot;
import com.maciej916.indreb.common.enums.GuiSlotType;
import com.maciej916.indreb.common.enums.InventorySlotType;
import com.maciej916.indreb.common.interfaces.entity.IExpCollector;
import com.maciej916.indreb.common.registries.ModBlockEntities;
import java.util.ArrayList;
import java.util.Arrays;
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
import net.minecraft.world.level.block.entity.FurnaceBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraftforge.common.ForgeHooks;
import net.minecraftforge.common.capabilities.Capability;
import net.minecraftforge.common.util.LazyOptional;
import net.minecraftforge.items.CapabilityItemHandler;
import net.minecraftforge.items.wrapper.RangedWrapper;

public class BlockEntityIronFurnace extends IndRebBlockEntity implements IExpCollector {
   public static final int FUEL_SLOT = 0;
   public static final int INPUT_SLOT = 1;
   public static final int OUTPUT_SLOT = 2;
   public BlockEntityProgress smelting = new BlockEntityProgress();
   public BlockEntityProgress fuel = new BlockEntityProgress();
   private boolean active = false;
   private ItemStack cachedInputStack = ItemStack.f_41583_;
   private ItemStack resultStack = ItemStack.f_41583_;
   private SmeltingRecipe furnaceRecipe;
   private final ArrayList<LazyOptional<?>> capabilities = new ArrayList<>(
      Arrays.asList(
         LazyOptional.of(this::getStackHandler),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 0, 1)),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 1, 2)),
         LazyOptional.of(() -> new RangedWrapper(this.getStackHandler(), 2, 3))
      )
   );

   public BlockEntityIronFurnace(BlockPos pWorldPosition, BlockState pBlockState) {
      super(ModBlockEntities.IRON_FURNACE, pWorldPosition, pBlockState);
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
      this.fuel.clearChanged();
      this.smelting.clearChanged();
      ItemStack inputStack = this.getStackHandler().getStackInSlot(1);
      if (this.cachedInputStack.m_41720_() != inputStack.m_41720_()) {
         this.cachedInputStack = inputStack.m_41777_();
         if (inputStack.m_41720_() != Items.f_41852_ && this.getRecipe(inputStack).isPresent()) {
            this.furnaceRecipe = this.getRecipe(this.cachedInputStack).orElseThrow();
            this.resultStack = this.getRecipeResult(inputStack);
         } else {
            this.furnaceRecipe = null;
         }
      }

      ItemStack fuelItemStack = this.getStackHandler().getStackInSlot(0);
      ItemStack outputItemStack = this.getStackHandler().getStackInSlot(2);
      if (this.fuel.getProgress() > 0.0F) {
         this.active = true;
         this.fuel.decProgress(1.0F);
         if (this.cachedInputStack.m_41619_()) {
            this.smelting.setBoth(-1.0F);
         } else if (this.canSmelt(inputStack, outputItemStack, this.resultStack)) {
            if (this.smelting.getProgress() == -1.0F) {
               this.smelting.setData(0.0F, (float)((int)((double)this.getSmeltTime() * 0.8)));
            } else {
               this.smelting.incProgress(1.0F);
               if (this.smelting.getProgress() >= this.smelting.getProgressMax()) {
                  if (outputItemStack.m_41619_()) {
                     this.getStackHandler().setStackInSlot(2, this.resultStack.m_41777_());
                  } else {
                     outputItemStack.m_41769_(1);
                     this.getStackHandler().setStackInSlot(2, outputItemStack);
                  }

                  inputStack.m_41774_(1);
                  this.getStackHandler().setStackInSlot(1, inputStack);
                  this.setRecipeUsed(this.furnaceRecipe);
                  this.smelting.setBoth(-1.0F);
               }
            }
         }
      } else {
         this.active = false;
         this.fuel.setBoth(-1.0F);
         if (this.smelting.getProgress() > 0.0F) {
            this.smelting.decProgress(1.0F);
         }

         if (this.canSmelt(inputStack, outputItemStack, this.resultStack)) {
            int burnTime = ForgeHooks.getBurnTime(fuelItemStack, RecipeType.f_44108_);
            if (burnTime > 0) {
               this.fuel.setBoth((float)((int)((double)burnTime * 1.2)));
               fuelItemStack.m_41774_(1);
               this.active = true;
            }
         }
      }

      this.setActive(this.active);
      if (this.fuel.changed() || this.smelting.changed()) {
         super.updateBlockState();
      }
   }

   @Override
   public boolean isItemValidForSlot(int slot, @Nonnull ItemStack stack) {
      if (slot == 1) {
         return this.isValidInput(stack);
      } else {
         return slot == 0 ? FurnaceBlockEntity.m_58399_(stack) : false;
      }
   }

   @Override
   public void m_142466_(CompoundTag tag) {
      super.m_142466_(tag);
      this.active = tag.m_128471_("active");
      this.smelting.deserializeNBT(tag.m_128469_("smelting"));
      this.fuel.deserializeNBT(tag.m_128469_("fuel"));
   }

   @Override
   public CompoundTag save(CompoundTag tag) {
      tag.m_128379_("active", this.active);
      tag.m_128365_("smelting", this.smelting.serializeNBT());
      tag.m_128365_("fuel", this.fuel.serializeNBT());
      return super.save(tag);
   }

   @Override
   public ArrayList<IndRebSlot> addInventorySlot(ArrayList<IndRebSlot> slots) {
      slots.add(new IndRebSlot(1, 56, 17, InventorySlotType.INPUT, GuiSlotType.NORMAL, 55, 16));
      slots.add(new IndRebSlot(0, 56, 53, InventorySlotType.INPUT, GuiSlotType.NORMAL, 55, 52));
      slots.add(new IndRebSlot(2, 116, 35, InventorySlotType.OUTPUT, GuiSlotType.LARGE, 111, 30));
      return super.addInventorySlot(slots);
   }

   @Override
   public float getExperience(Recipe<?> recipe) {
      return ((SmeltingRecipe)recipe).m_43750_();
   }

   public boolean hasExpButton() {
      return false;
   }

   @Nonnull
   @Override
   public <T> LazyOptional<T> getCapability(@Nonnull Capability<T> cap, @Nullable Direction side) {
      if (cap == CapabilityItemHandler.ITEM_HANDLER_CAPABILITY) {
         if (side == null) {
            return this.capabilities.get(0).cast();
         } else {
            return switch (side) {
               case UP -> this.capabilities.get(2).cast();
               case DOWN -> this.capabilities.get(3).cast();
               default -> this.capabilities.get(1).cast();
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
}
