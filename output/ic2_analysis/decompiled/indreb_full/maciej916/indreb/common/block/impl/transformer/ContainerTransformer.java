package com.maciej916.indreb.common.block.impl.transformer;

import com.maciej916.indreb.common.container.IndRebContainer;
import com.maciej916.indreb.common.registries.ModContainers;
import net.minecraft.core.BlockPos;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;

public class ContainerTransformer extends IndRebContainer {
   public ContainerTransformer(int windowId, Inventory inv, FriendlyByteBuf data) {
      this(windowId, inv.f_35978_.m_20193_(), data.m_130135_(), inv, inv.f_35978_);
   }

   public ContainerTransformer(int windowId, Level world, BlockPos pos, Inventory playerInventory, Player player) {
      super(ModContainers.TRANSFORMER, windowId, world, pos, playerInventory, player);
   }
}
