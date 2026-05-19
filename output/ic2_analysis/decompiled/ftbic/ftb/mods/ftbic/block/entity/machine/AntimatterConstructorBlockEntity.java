package dev.ftb.mods.ftbic.block.entity.machine;

import dev.ftb.mods.ftbic.FTBICConfig;
import dev.ftb.mods.ftbic.block.FTBICElectricBlocks;
import dev.ftb.mods.ftbic.block.entity.ElectricBlockEntity;
import dev.ftb.mods.ftbic.item.FTBICItems;
import dev.ftb.mods.ftbic.recipe.RecipeCache;
import dev.ftb.mods.ftbic.screen.AntimatterConstructorMenu;
import dev.ftb.mods.ftbic.screen.sync.SyncedData;
import dev.ftb.mods.ftbic.screen.sync.SyncedDataKey;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.ItemLike;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.NotNull;

public class AntimatterConstructorBlockEntity extends ElectricBlockEntity {
   public static final SyncedDataKey<Boolean> HAS_BOOST = new SyncedDataKey("has_boost", false);
   public double boost = 0.0;
   private boolean hasBoost = false;

   public AntimatterConstructorBlockEntity(BlockPos pos, BlockState state) {
      super(FTBICElectricBlocks.ANTIMATTER_CONSTRUCTOR, pos, state);
   }

   @Override
   public void writeData(CompoundTag tag) {
      super.writeData(tag);
      tag.m_128347_("Boost", this.boost);
   }

   @Override
   public void readData(CompoundTag tag) {
      super.readData(tag);
      this.boost = tag.m_128459_("Boost");
   }

   @Override
   public void tick() {
      super.tick();
      if (this.energy >= this.energyCapacity) {
         if (this.outputItems[0].m_41619_()) {
            this.outputItems[0] = new ItemStack((ItemLike)FTBICItems.ANTIMATTER.item.get());
            this.energy = this.energy - this.energyCapacity;
            this.m_6596_();
         } else if (this.outputItems[0].m_41613_() < this.outputItems[0].m_41741_()) {
            this.outputItems[0].m_41769_(1);
            this.energy = this.energy - this.energyCapacity;
            this.m_6596_();
         }
      } else if (this.boost <= 0.0) {
         this.boost = this.getBoost(this.inputItems[0]);
         if (this.boost > 0.0) {
            this.inputItems[0].m_41774_(1);
            if (this.inputItems[0].m_41619_()) {
               this.inputItems[0] = ItemStack.f_41583_;
            }

            this.m_6596_();
         }
      }

      this.hasBoost = this.boost > 0.0;
   }

   @Override
   public boolean isItemValid(int slot, @NotNull ItemStack stack) {
      return slot == 0 && this.getBoost(stack) > 0.0;
   }

   private double getBoost(ItemStack item) {
      RecipeCache recipeCache = this.getRecipeCache();
      return recipeCache == null ? 0.0 : recipeCache.getAntimatterBoost(this.f_58857_, item);
   }

   public double insertEnergy(double maxInsert, boolean simulate) {
      if (this.energy >= this.energyCapacity) {
         return 0.0;
      } else {
         if (!simulate) {
            double boosted = Math.min(this.boost, maxInsert);
            this.boost -= boosted;
            maxInsert -= boosted;
            this.energy = this.energy + boosted * (Double)FTBICConfig.MACHINES.ANTIMATTER_CONSTRUCTOR_BOOST.get() + maxInsert;
         }

         return maxInsert;
      }
   }

   @Override
   public InteractionResult rightClick(Player player, InteractionHand hand, BlockHitResult hit) {
      if (!this.f_58857_.m_5776_()) {
         this.openMenu((ServerPlayer)player, (id, inventory) -> new AntimatterConstructorMenu(id, inventory, this));
      }

      return InteractionResult.SUCCESS;
   }

   @Override
   public void addSyncData(SyncedData data) {
      super.addSyncData(data);
      data.addBoolean(HAS_BOOST, () -> this.hasBoost);
   }
}
