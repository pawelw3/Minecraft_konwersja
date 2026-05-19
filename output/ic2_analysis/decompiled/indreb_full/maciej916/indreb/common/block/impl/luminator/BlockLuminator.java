package com.maciej916.indreb.common.block.impl.luminator;

import com.maciej916.indreb.common.block.IndRebEntityBlock;
import com.maciej916.indreb.common.interfaces.block.IStateActive;
import com.maciej916.indreb.common.util.BlockStateHelper;
import com.maciej916.indreb.common.util.wrench.WrenchHelper;
import javax.annotation.Nullable;
import net.minecraft.core.BlockPos;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.BlockBehaviour.Properties;
import net.minecraft.world.level.material.Material;
import net.minecraft.world.level.material.MaterialColor;

public class BlockLuminator extends IndRebEntityBlock implements IStateActive {
   public BlockLuminator() {
      super(Properties.m_60944_(Material.f_76275_, MaterialColor.f_76401_).m_60953_(state -> state.m_61143_(BlockStateHelper.activeProperty) ? 16 : 0));
      WrenchHelper.registerAction(this).add(WrenchHelper.dropAction());
   }

   @Nullable
   public BlockEntity m_142194_(BlockPos pos, BlockState state) {
      return new BlockEntityLuminator(pos, state);
   }
}
