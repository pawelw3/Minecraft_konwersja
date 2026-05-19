package dev.ftb.mods.ftbic.block.entity.machine;

import dev.ftb.mods.ftbic.block.entity.ElectricBlockEntity;
import dev.ftb.mods.ftbic.item.UpgradeItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraftforge.items.ItemStackHandler;
import org.jetbrains.annotations.NotNull;

public class UpgradeInventory extends ItemStackHandler {
   public final ElectricBlockEntity entity;
   public final int limit;

   public UpgradeInventory(ElectricBlockEntity e, int slots, int stackLimit) {
      super(slots);
      this.entity = e;
      this.limit = stackLimit;
   }

   protected void onContentsChanged(int slot) {
      if (this.entity.m_58898_() && !this.entity.m_58904_().m_5776_()) {
         this.entity.initProperties();
         this.entity.upgradesChanged();
         this.entity.m_6596_();
      }
   }

   public boolean isItemValid(int slot, @NotNull ItemStack stack) {
      return stack.m_41720_() instanceof UpgradeItem;
   }

   public int getSlotLimit(int slot) {
      return this.limit;
   }

   public int countUpgrades(Item item) {
      int count = 0;

      for (int i = 0; i < this.getSlots(); i++) {
         ItemStack stack = this.getStackInSlot(i);
         if (stack.m_41720_() == item) {
            count += stack.m_41613_();
         }
      }

      return count;
   }
}
