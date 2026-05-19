package dev.ftb.mods.ftbic.block.entity.generator;

import dev.ftb.mods.ftbic.block.FTBICElectricBlocks;
import dev.ftb.mods.ftbic.recipe.RecipeCache;
import dev.ftb.mods.ftbic.screen.BasicGeneratorMenu;
import dev.ftb.mods.ftbic.screen.sync.SyncedData;
import dev.ftb.mods.ftbic.screen.sync.SyncedDataKey;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.NotNull;

public class BasicGeneratorBlockEntity extends GeneratorBlockEntity {
   public static final SyncedDataKey<Integer> FUEL_BAR = new SyncedDataKey("fuel_ticks", 0);
   public int fuelTicks = 0;
   public int maxFuelTicks = 0;

   public BasicGeneratorBlockEntity(BlockPos pos, BlockState state) {
      super(FTBICElectricBlocks.BASIC_GENERATOR, pos, state);
   }

   @Override
   public void writeData(CompoundTag tag) {
      super.writeData(tag);
      tag.m_128405_("FuelTicks", this.fuelTicks);
      tag.m_128405_("MaxFuelTicks", this.maxFuelTicks);
   }

   @Override
   public void readData(CompoundTag tag) {
      super.readData(tag);
      this.fuelTicks = tag.m_128451_("FuelTicks");
      this.maxFuelTicks = tag.m_128451_("MaxFuelTicks");
   }

   @Override
   public boolean isItemValid(int slot, @NotNull ItemStack stack) {
      if (slot != 0) {
         return false;
      } else {
         RecipeCache recipeCache = this.getRecipeCache();
         return recipeCache != null && recipeCache.getBasicGeneratorFuelTicks(this.f_58857_, stack) > 0;
      }
   }

   @Override
   public void handleGeneration() {
      if (this.fuelTicks > 0) {
         this.fuelTicks--;
         if (this.energy < this.energyCapacity) {
            this.energy = this.energy + Math.min(this.energyCapacity - this.energy, this.maxEnergyOutput);
         }

         if (this.fuelTicks == 0) {
            this.m_6596_();
         }
      }

      if (this.fuelTicks == 0 && this.energy < this.energyCapacity && !this.inputItems[0].m_41619_()) {
         RecipeCache recipeCache = this.getRecipeCache();
         if (recipeCache != null) {
            this.maxFuelTicks = recipeCache.getBasicGeneratorFuelTicks(this.f_58857_, this.inputItems[0]);
            this.fuelTicks = this.maxFuelTicks;
            if (this.maxFuelTicks > 0) {
               if (this.inputItems[0].m_41613_() == 1) {
                  this.inputItems[0] = this.inputItems[0].getContainerItem();
               } else {
                  this.inputItems[0].m_41774_(1);
               }

               this.active = true;
               this.m_6596_();
            }
         }
      }
   }

   @Override
   public InteractionResult rightClick(Player player, InteractionHand hand, BlockHitResult hit) {
      if (!this.f_58857_.m_5776_()) {
         this.openMenu((ServerPlayer)player, (id, inventory) -> new BasicGeneratorMenu(id, inventory, this));
      }

      return InteractionResult.SUCCESS;
   }

   @Override
   public void addSyncData(SyncedData data) {
      super.addSyncData(data);
      data.addShort(
         SyncedData.BAR, () -> this.fuelTicks == 0 ? 0 : Mth.m_14045_(Mth.m_14165_((double)this.fuelTicks * 14.0 / (double)this.maxFuelTicks), 0, 14)
      );
   }
}
