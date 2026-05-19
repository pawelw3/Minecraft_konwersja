package dev.ftb.mods.ftbic.block.entity.machine;

import dev.ftb.mods.ftbic.FTBICConfig;
import dev.ftb.mods.ftbic.block.ElectricBlockInstance;
import dev.ftb.mods.ftbic.recipe.MachineRecipeResults;
import dev.ftb.mods.ftbic.recipe.MachineRecipeSerializer;
import dev.ftb.mods.ftbic.recipe.RecipeCache;
import dev.ftb.mods.ftbic.recipe.SimpleMachineRecipeResults;
import dev.ftb.mods.ftbic.screen.MachineMenu;
import dev.ftb.mods.ftbic.screen.sync.SyncedData;
import dev.ftb.mods.ftbic.util.MachineProcessingResult;
import java.util.Random;
import net.minecraft.Util;
import net.minecraft.core.BlockPos;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.chat.TextComponent;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraftforge.items.ItemHandlerHelper;
import net.minecraftforge.items.ItemStackHandler;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

public abstract class MachineBlockEntity extends BasicMachineBlockEntity {
   public double progress = 0.0;
   public double maxProgress = 0.0;
   public int acceleration = 0;
   private boolean checkProcessing = true;
   public boolean shouldAccelerate;

   public MachineBlockEntity(ElectricBlockInstance type, BlockPos pos, BlockState state) {
      super(type, pos, state);
   }

   @Override
   public void writeData(CompoundTag tag) {
      super.writeData(tag);
      tag.m_128347_("MaxProgress", this.maxProgress);
      tag.m_128347_("Progress", this.progress);
      if (this.acceleration > 0) {
         tag.m_128405_("Acceleration", this.acceleration);
      }
   }

   @Override
   public void readData(CompoundTag tag) {
      super.readData(tag);
      this.maxProgress = tag.m_128459_("MaxProgress");
      this.progress = tag.m_128459_("Progress");
      this.acceleration = tag.m_128451_("Acceleration");
   }

   @Nullable
   private ItemStackHandler getOutput(MachineProcessingResult result, boolean simulate) {
      ItemStackHandler output = new ItemStackHandler(NonNullList.m_122780_(this.outputItems.length, ItemStack.f_41583_));

      for (int i = 0; i < this.outputItems.length; i++) {
         output.setStackInSlot(i, this.outputItems[i].m_41777_());
      }

      Random random = this.f_58857_ != null ? this.f_58857_.f_46441_ : new Random();
      if ((simulate || random.nextDouble() < result.output.chance)
         && !ItemHandlerHelper.insertItemStacked(output, result.output.stack.m_41777_(), false).m_41619_()) {
         return null;
      } else {
         for (int i = 0; i < result.extra.length; i++) {
            if (result.extra[i].chance >= 1.0) {
               if (!ItemHandlerHelper.insertItemStacked(output, result.extra[i].stack.m_41777_(), false).m_41619_()) {
                  return null;
               }
            } else if (!simulate
               && random.nextDouble() < result.extra[i].chance
               && !ItemHandlerHelper.insertItemStacked(output, result.extra[i].stack.m_41777_(), false).m_41619_()) {
               return null;
            }
         }

         return output;
      }
   }

   @Override
   public void handleProcessing() {
      if (!this.isBurnt() && !this.f_58857_.m_5776_()) {
         if (this.maxProgress > 0.0 && this.progress < this.maxProgress) {
            int eu = Mth.m_14165_(this.energyUse);
            if (eu > 0 && this.energy >= (double)eu) {
               this.progress = this.progress + this.progressSpeed;
               this.energy -= (double)eu;
               this.active = true;
               if (this.energy < (double)eu) {
                  this.m_6596_();
               }

               if (this.shouldAccelerate) {
                  this.acceleration++;
               }
            }

            if (this.progress >= this.maxProgress) {
               this.progress = 0.0;
               this.m_6596_();
               this.shiftInputs();
               MachineProcessingResult result = this.getResult(this.inputItems, true);
               if (result.exists()) {
                  ItemStackHandler out = this.getOutput(result, false);
                  if (out != null) {
                     for (int i = 0; i < result.consume.length; i++) {
                        this.inputItems[i].m_41774_(result.consume[i]);
                        if (this.inputItems[i].m_41619_()) {
                           this.inputItems[i] = ItemStack.f_41583_;
                        }
                     }

                     for (int ix = 0; ix < this.outputItems.length; ix++) {
                        this.outputItems[ix] = out.getStackInSlot(ix);
                     }

                     this.shiftInputs();
                     this.ejectOutputItems();
                  }
               }

               this.checkProcessing = true;
            }
         }

         if (this.checkProcessing) {
            this.checkProcessing = false;
            MachineProcessingResult result = this.getResult(this.inputItems, true);
            boolean hasResult = result.exists() && this.getOutput(result, true) != null;
            if (!hasResult) {
               this.progress = 0.0;
               this.maxProgress = 0.0;
               this.m_6596_();
            } else if (this.progress <= 0.0) {
               this.maxProgress = result.time * (Double)FTBICConfig.MACHINES.MACHINE_RECIPE_BASE_TICKS.get();
               this.active = true;
               this.m_6596_();
            }
         }

         if (this.acceleration > 0) {
            this.acceleration--;
            if (this.acceleration == 0) {
               this.m_6596_();
            }
         }
      }
   }

   @Override
   public void inventoryChanged(int slot, @Nullable ItemStack prev) {
      super.inventoryChanged(slot, prev);
      this.checkProcessing = true;
   }

   @Override
   public void energyChanged(int prev) {
      super.energyChanged(prev);
      if (this.energyUse != 0.0 && (double)prev < this.energyUse && this.energy >= this.energyUse) {
         this.checkProcessing = true;
      }
   }

   public abstract MachineRecipeResults getRecipes(RecipeCache var1);

   public MachineProcessingResult getResult(ItemStack[] items, boolean checkCount) {
      RecipeCache cache = this.getRecipeCache();
      return cache != null ? this.getRecipes(cache).getResult(this.f_58857_, items, checkCount) : MachineProcessingResult.NONE;
   }

   @Override
   public boolean isItemValid(int slot, @NotNull ItemStack stack) {
      RecipeCache cache = this.getRecipeCache();
      return cache != null && this.getRecipes(cache).canInsert(this.f_58857_, slot, stack);
   }

   @Nullable
   public MachineRecipeSerializer getRecipeSerializer() {
      RecipeCache cache = this.getRecipeCache();
      MachineRecipeResults results = cache == null ? null : this.getRecipes(cache);
      return results instanceof SimpleMachineRecipeResults ? (MachineRecipeSerializer)((SimpleMachineRecipeResults)results).recipeSerializer.get() : null;
   }

   @Override
   public InteractionResult rightClick(Player player, InteractionHand hand, BlockHitResult hit) {
      if (!this.f_58857_.m_5776_()) {
         MachineRecipeSerializer serializer = this.getRecipeSerializer();
         if (serializer != null) {
            this.openMenu((ServerPlayer)player, (id, inventory) -> new MachineMenu(id, inventory, this, serializer));
         } else {
            player.m_6352_(new TextComponent("No GUI yet!"), Util.f_137441_);
         }
      }

      return InteractionResult.SUCCESS;
   }

   @Override
   public void writeMenu(ServerPlayer player, FriendlyByteBuf buf) {
      super.writeMenu(player, buf);
      buf.m_130085_(this.getRecipeSerializer().getRegistryName());
   }

   @Override
   public void addSyncData(SyncedData data) {
      super.addSyncData(data);
      data.addShort(SyncedData.BAR, () -> this.energyUse == 0.0 ? 0 : Mth.m_14045_(Mth.m_14165_(this.progress * 24.0 / this.maxProgress), 0, 24));
      data.addShort(SyncedData.ACCELERATION, () -> this.acceleration);
   }

   @Override
   public void initProperties() {
      super.initProperties();
      this.shouldAccelerate = false;
   }
}
