package dev.ftb.mods.ftbic.block.entity.machine;

import com.google.gson.JsonElement;
import dev.ftb.mods.ftbic.FTBIC;
import dev.ftb.mods.ftbic.block.FTBICElectricBlocks;
import dev.ftb.mods.ftbic.screen.PoweredCraftingTableMenu;
import dev.ftb.mods.ftbic.screen.sync.SyncedData;
import dev.ftb.mods.ftbic.util.FTBICUtils;
import java.util.Arrays;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.crafting.Ingredient;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.BlockHitResult;
import org.jetbrains.annotations.NotNull;

public class PoweredCraftingTableBlockEntity extends BasicMachineBlockEntity {
   public final Ingredient[] ingredients = new Ingredient[9];
   private ResourceLocation matchedRecipe;
   public double progress;

   public PoweredCraftingTableBlockEntity(BlockPos pos, BlockState state) {
      super(FTBICElectricBlocks.POWERED_CRAFTING_TABLE, pos, state);
      Arrays.fill(this.ingredients, Ingredient.f_43901_);
   }

   @Override
   public void writeData(CompoundTag tag) {
      super.writeData(tag);

      for (int i = 0; i < 9; i++) {
         if (this.ingredients[i] != Ingredient.f_43901_) {
            tag.m_128359_("Ingredient" + (i + 1), FTBICUtils.GSON.toJson(this.ingredients[i].m_43942_()));
         }
      }
   }

   @Override
   public void readData(CompoundTag tag) {
      super.readData(tag);
      Arrays.fill(this.ingredients, Ingredient.f_43901_);

      for (int i = 0; i < 9; i++) {
         String s = tag.m_128461_("Ingredient" + (i + 1));
         this.ingredients[i] = s.isEmpty() ? Ingredient.f_43901_ : Ingredient.m_43917_((JsonElement)FTBICUtils.GSON.fromJson(s, JsonElement.class));
      }

      this.matchedRecipe = null;
   }

   @Override
   public boolean isItemValid(int slot, @NotNull ItemStack stack) {
      return slot >= 0 && slot < 9 && this.ingredients[slot] != Ingredient.f_43901_ && this.ingredients[slot].test(stack);
   }

   @Override
   public int getSlotLimit(int slot) {
      return slot < 9 ? 1 : 64;
   }

   @Override
   public void writeMenu(ServerPlayer player, FriendlyByteBuf buf) {
      super.writeMenu(player, buf);

      for (int i = 0; i < 9; i++) {
         this.ingredients[i].m_43923_(buf);
      }
   }

   @Override
   public void handleProcessing() {
      if (!(this.energy < this.energyUse)) {
         boolean hasRecipe = false;

         for (int i = 0; i < this.ingredients.length; i++) {
            if (this.ingredients[i] == Ingredient.f_43901_) {
               if (!this.inputItems[i].m_41619_()) {
                  return;
               }
            } else {
               hasRecipe = true;
               if (this.inputItems[i].m_41619_() || !this.ingredients[i].test(this.inputItems[i])) {
                  return;
               }
            }
         }

         if (hasRecipe) {
            this.progress = this.progress + this.progressSpeed;
            this.energy = this.energy - this.energyUse;
            if (this.progress >= 100.0) {
               this.progress = 0.0;
               FTBIC.LOGGER.info("Success!");
               this.m_6596_();
            }
         }
      }
   }

   @Override
   public InteractionResult rightClick(Player player, InteractionHand hand, BlockHitResult hit) {
      if (!this.f_58857_.m_5776_()) {
         this.openMenu((ServerPlayer)player, (id, inventory) -> new PoweredCraftingTableMenu(id, inventory, this));
      }

      return InteractionResult.SUCCESS;
   }

   @Override
   public void addSyncData(SyncedData data) {
      super.addSyncData(data);
      data.addShort(SyncedData.BAR, () -> Mth.m_14165_(this.progress * 22.0 / 100.0));
   }
}
